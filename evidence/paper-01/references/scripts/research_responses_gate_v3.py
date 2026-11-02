"""Responses wire gate for a controller-owned, text-only research sender.

No authentication, HTTP client or executor. Reuses the tested journal protocol.
"""
import base64
from dataclasses import asdict
import sys
import research_dual_gate_v1 as core
import research_response_capacity_v1 as capacity

VERSION = core.VERSION
MAX_BYTES = capacity.MAX_RESPONSE_BYTES
encode = core.encode
sha = core.sha
Rejected = core.Rejected
strict = core.strict
validate_local_input = core.validate_input


def validate_input(raw, ticket):
    obj = strict(raw)
    if core.has_tool_definitions(obj):
        raise Rejected('TOOL_DEFINITIONS_PRESENT')
    required = {'model', 'input', 'tools', 'tool_choice', 'parallel_tool_calls', 'reasoning', 'store', 'stream'}
    if set(obj) != required:
        raise Rejected('UNSUPPORTED_REQUEST_FIELDS')
    if obj['parallel_tool_calls'] is not False or obj['store'] is not False or obj['stream'] is not True or obj['reasoning'] != {'effort': 'medium'}:
        raise Rejected('INVALID_TRANSPORT_SETTINGS')
    local = encode({key: obj[key] for key in ['model', 'input', 'tools', 'tool_choice']})
    # Reuse the strict message/content contract; bind to the full wire bytes below.
    validate_local_input(local, {**ticket, 'request_sha256': sha(local)})
    if sha(raw) != ticket['request_sha256']:
        raise Rejected('PLANNED_BYTES_MISMATCH')


def output_item(item, *, final=False):
    if type(item) is not dict:
        raise Rejected('INVALID_OUTPUT_ITEM')
    kind = item.get('type')
    if kind not in ('message', 'reasoning'):
        raise Rejected('NON_TEXT_RESPONSE')
    common = {'type', 'id', 'status'}
    allowed = common | ({'role', 'content', 'phase'} if kind == 'message' else {'summary', 'content', 'encrypted_content'})
    if set(item) - allowed:
        raise Rejected('UNKNOWN_OUTPUT_FIELDS')
    if 'id' in item and type(item['id']) is not str:
        raise Rejected('INVALID_OUTPUT_ID')
    if final and item.get('status') not in (None, 'completed'):
        raise Rejected('INCOMPLETE_OUTPUT_ITEM')
    if kind == 'message':
        if item.get('role') != 'assistant' or type(item.get('content')) is not list:
            raise Rejected('INVALID_MESSAGE_OUTPUT')
        if item.get('phase') not in (None, 'final_answer'):
            raise Rejected('UNEXPECTED_MESSAGE_PHASE')
        for part in item['content']:
            content_part(part)
        if final and (not item['content'] or not any(p['text'].strip() for p in item['content'])):
            raise Rejected('EMPTY_OUTPUT')
    else:
        for key in ['summary', 'content']:
            if key not in item or item[key] is None:
                continue
            if type(item[key]) is not list:
                raise Rejected('INVALID_REASONING')
            for part in item[key]:
                if type(part) is not dict or set(part) != {'type', 'text'} or part['type'] not in ('summary_text', 'reasoning_text') or type(part['text']) is not str:
                    raise Rejected('INVALID_REASONING')
        if item.get('encrypted_content') is not None and type(item['encrypted_content']) is not str:
            raise Rejected('INVALID_REASONING')


def content_part(part):
    if type(part) is not dict or set(part) - {'type', 'text', 'annotations', 'logprobs'} or part.get('type') != 'output_text' or type(part.get('text')) is not str:
        raise Rejected('NON_TEXT_RESPONSE')
    if part.get('annotations', []) != [] or part.get('logprobs', []) not in ([], None):
        raise Rejected('UNSUPPORTED_TEXT_METADATA')


def parse_sse(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
        raise Rejected('INVALID_SIZE_OR_BYTES')
    try:
        text = raw.decode('utf-8').replace('\r\n', '\n')
    except UnicodeError:
        raise Rejected('INVALID_STREAM_ENCODING') from None
    if not text.endswith('\n\n'):
        raise Rejected('TRUNCATED_STREAM')
    events = []
    for block in text.split('\n\n'):
        if not block.strip():
            continue
        if len(block.encode()) > capacity.MAX_FRAME_BYTES:
            raise Rejected('SSE_FRAME_SIZE_LIMIT')
        data = []
        event_name = None
        for line in block.split('\n'):
            if line.startswith(':'):
                continue
            if line.startswith('data:'):
                data.append(line[5:].lstrip(' '))
            elif line.startswith('event:') and event_name is None:
                event_name = line[6:].strip()
            else:
                raise Rejected('UNKNOWN_SSE_FIELD')
        if not data:
            continue
        if len(events) >= capacity.MAX_EVENTS:
            raise Rejected('SSE_EVENT_COUNT_LIMIT')
        value = '\n'.join(data)
        if value == '[DONE]':
            events.append({'type': '__done__'})
            continue
        obj = strict(value.encode())
        if event_name and event_name != obj.get('type'):
            raise Rejected('SSE_EVENT_MISMATCH')
        events.append(obj)
    return events


def read_text(raw):
    events = parse_sse(raw)
    allowed = {'response.created', 'response.in_progress', 'response.output_item.added', 'response.output_item.done',
        'response.content_part.added', 'response.content_part.done', 'response.output_text.delta', 'response.output_text.done',
        'response.reasoning_summary_part.added', 'response.reasoning_summary_part.done',
        'response.reasoning_summary_text.delta', 'response.reasoning_summary_text.done',
        'response.reasoning_text.delta', 'response.reasoning_text.done', 'response.completed', '__done__'}
    added, done, deltas, text_done, parts_done = {}, {}, {}, {}, {}
    final = None
    delta_bytes = 0
    response_id = None
    for event in events:
        kind = event.get('type')
        if kind not in allowed:
            raise Rejected('UNKNOWN_OR_UNSAFE_STREAM_EVENT')
        if final is not None and kind != '__done__':
            raise Rejected('EVENT_AFTER_COMPLETION')
        if kind == '__done__':
            if final is None:
                raise Rejected('PREMATURE_DONE')
            continue
        if 'item' in event:
            output_item(event['item'], final=kind == 'response.output_item.done')
        if kind in ('response.created', 'response.in_progress', 'response.completed'):
            response = event.get('response')
            if type(response) is not dict or type(response.get('id')) is not str:
                raise Rejected('INVALID_RESPONSE_ENVELOPE')
            if response_id is None:
                response_id = response['id']
            if response['id'] != response_id:
                raise Rejected('RESPONSE_ID_MISMATCH')
            for item in response.get('output', []):
                output_item(item, final=kind == 'response.completed')
            if kind == 'response.completed':
                if response.get('status') != 'completed' or response.get('error') is not None or response.get('incomplete_details') is not None:
                    raise Rejected('INCOMPLETE_RESPONSE')
                final = response
        elif kind in ('response.output_item.added', 'response.output_item.done'):
            index = event.get('output_index')
            if type(index) is not int or index < 0:
                raise Rejected('INVALID_OUTPUT_INDEX')
            target = added if kind.endswith('added') else done
            if index in target:
                raise Rejected('DUPLICATE_OUTPUT_ITEM')
            target[index] = event['item']
        elif kind.startswith('response.content_part.'):
            content_part(event.get('part'))
            if kind.endswith('done'):
                key = (event.get('output_index'), event.get('content_index'))
                if any(type(v) is not int or v < 0 for v in key) or key in parts_done:
                    raise Rejected('INVALID_CONTENT_PART_SEQUENCE')
                parts_done[key] = event['part']
        elif kind.startswith('response.output_text.'):
            key = (event.get('output_index'), event.get('content_index'))
            if any(type(v) is not int or v < 0 for v in key):
                raise Rejected('INVALID_TEXT_INDEX')
            if kind.endswith('delta'):
                if type(event.get('delta')) is not str:
                    raise Rejected('INVALID_DELTA')
                delta_bytes += len(event['delta'].encode())
                if delta_bytes > capacity.MAX_TEXT_BYTES:
                    raise Rejected('TEXT_SIZE_LIMIT')
                deltas[key] = deltas.get(key, '') + event['delta']
            else:
                if key in text_done or type(event.get('text')) is not str:
                    raise Rejected('INVALID_TEXT_DONE')
                text_done[key] = event['text']
        # Reasoning events are stored but never executed, forwarded or interpreted.
    if final is None or type(final.get('output')) is not list:
        raise Rejected('MISSING_COMPLETION')
    # Observed Codex variant: completion omits the already-streamed output items.
    # Require a complete contiguous added/done sequence; never repair text.
    items = final['output']
    if not items:
        if set(done) != set(range(len(done))) or not done:
            raise Rejected('INCOMPLETE_COMPACT_OUTPUT')
        items = [done[i] for i in range(len(done))]
    expected_indexes = set(range(len(items)))
    if set(done) != expected_indexes or set(added) != expected_indexes:
        raise Rejected('INCOMPLETE_ITEM_SEQUENCE')
    texts = {}
    for index, item in enumerate(items):
        if item != done[index] or item.get('id') != added[index].get('id') or item['type'] != added[index]['type']:
            raise Rejected('STREAM_FINAL_MISMATCH')
        if item['type'] == 'message':
            for ci, part in enumerate(item['content']):
                texts[index, ci] = part['text']
                if parts_done.get((index, ci)) != part:
                    raise Rejected('CONTENT_PART_STREAM_MISMATCH')
    if len([v for v in items if v['type'] == 'message']) != 1 or not texts:
        raise Rejected('EXPECTED_ONE_TEXT_MESSAGE')
    if set(parts_done) != set(texts) or text_done != texts or any(key not in texts or value != texts[key] for key, value in deltas.items()):
        raise Rejected('TEXT_STREAM_MISMATCH')
    text = ''.join(texts[key] for key in sorted(texts))
    if len(text.encode()) > capacity.MAX_TEXT_BYTES:
        raise Rejected('TEXT_SIZE_LIMIT')
    return text


def validate_output(raw):
    read_text(raw)


class ResponsesRunner(core.GuardedRunner):
    """Same durable claim/send order, with the raw SSE checked before decoding."""
    def run(self, trial, raw):
        if trial not in self.plan or type(raw) is not bytes:
            try:
                self.journal.note(str(trial)[:64], 'rejected', b'UNKNOWN_TRIAL_OR_MUTABLE_INPUT')
            except Exception:
                return core.Result('JOURNAL_UNAVAILABLE', 'BEFORE_SEND', False)
            return core.Result('INPUT_REJECTED', 'UNKNOWN_TRIAL_OR_MUTABLE_INPUT', False)
        try:
            self.journal.claim(trial, raw)
        except core.Replay:
            return core.Result('REPLAY_BLOCKED', 'ALREADY_CLAIMED', False)
        except Exception:
            return core.Result('JOURNAL_UNAVAILABLE', 'BEFORE_SEND', False)
        binding = {'run_id': self.run_id, 'trial_id': trial, 'plan_sha256': self.plan_hash, **asdict(self.plan[trial])}
        try:
            result = self.gate.check('input', raw, binding)
            self.journal.note(trial, 'input_gate', encode({'verdict': result.verdict, 'reason': result.reason,
                'stdout': base64.b64encode(result.stdout).decode(), 'stderr': base64.b64encode(result.stderr).decode()}))
        except Exception:
            return self._finish(trial, 'GATE_UNAVAILABLE', 'INPUT_GATE_OR_AUDIT_FAILURE', False)
        if result.verdict != 'PASS':
            return self._finish(trial, 'INPUT_REJECTED' if result.verdict == 'REJECT' else 'GATE_UNAVAILABLE', result.reason, False)
        try:
            self.journal.send_intent(trial, raw)
        except Exception:
            return core.Result('JOURNAL_UNAVAILABLE', 'BEFORE_SEND', False)
        try:
            response = self.transport.send(raw)
        except Exception:
            return self._finish(trial, 'SEND_UNCERTAIN', 'TRANSPORT_RAISED', True)
        if type(response) is not bytes:
            return self._finish(trial, 'OUTPUT_REJECTED', 'NON_BYTES_RESPONSE', True)
        try:
            self.journal.state(trial, 'RAW_RECEIVED', response)
        except Exception:
            return core.Result('JOURNAL_UNAVAILABLE', 'AFTER_SEND', True)
        try:
            result = self.gate.check('output', response, binding)
            self.journal.note(trial, 'output_gate', encode({'verdict': result.verdict, 'reason': result.reason,
                'stdout': base64.b64encode(result.stdout).decode(), 'stderr': base64.b64encode(result.stderr).decode()}))
        except Exception:
            return self._finish(trial, 'GATE_UNAVAILABLE', 'OUTPUT_GATE_OR_AUDIT_FAILURE', True)
        if result.verdict != 'PASS':
            status = ('TOOL_REQUEST_BLOCKED' if result.reason == 'NON_TEXT_RESPONSE' else 'OUTPUT_REJECTED') if result.verdict == 'REJECT' else 'GATE_UNAVAILABLE'
            return self._finish(trial, status, result.reason, True)
        try:
            text = read_text(response)
        except Exception:
            return self._finish(trial, 'OUTPUT_REJECTED', 'DECODE_AFTER_GATE_FAILURE', True)
        return self._finish(trial, 'ACCEPTED', None, True, text)


if __name__ == '__main__':
    if sys.argv[1:] != ['--gate']:
        raise SystemExit('Only --gate is supported.')
    capacity.gate_main(validate_input, validate_output)
