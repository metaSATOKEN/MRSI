{
  "protocol": "SUMMARY-TIMING-01/v0.1",
  "status": "DESIGN_ONLY_NO_MODEL_EXECUTION",
  "seed": 2026092903,
  "conditions": {
    "LATE": {
      "summary_stages": [
        "USE"
      ]
    },
    "EARLY": {
      "summary_stages": [
        "FORM",
        "CONFIRM",
        "RECHECK",
        "USE",
        "RECHECK_DIAGNOSTIC"
      ]
    }
  },
  "source_materials": {
    "path": "study2/designs/counter-recheck-01-20260929/materials-proposal.json",
    "sha256": "002487f9c2d45a87c31eefb0afddfc158c427a92287c7531dce1ef53d0b21ce5",
    "known_materials": true,
    "all_eight_reused": true,
    "prior_model_answers_reused": false
  },
  "cases": [
    {
      "id": "N01",
      "proposer": "A",
      "peer": "B",
      "strength": "WEAK",
      "same_personal": true,
      "role_order": [
        "A",
        "B"
      ],
      "medium_order": [
        "PAPER",
        "DIGITAL"
      ],
      "experiences": [
        {
          "episode_id": "ED81AAE200D",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 6,
          "digital_success": 10
        },
        {
          "episode_id": "EFB9B239791",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 9,
          "digital_success": 16
        },
        {
          "episode_id": "E5A03A1A255",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 9,
          "digital_success": 7
        },
        {
          "episode_id": "E6A5E6E3A8F",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 18,
          "digital_success": 15
        },
        {
          "episode_id": "E22BFDC1C77",
          "observer": "A",
          "site": "区画1",
          "session": 3,
          "attempts_per_medium": 40,
          "paper_success": 21,
          "digital_success": 4
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "X",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 40
        },
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 42
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "PAPER",
          "B": "PAPER"
        },
        "projected_per_40": {
          "A": {
            "PAPER": 18,
            "DIGITAL": 15
          },
          "B": {
            "PAPER": 27,
            "DIGITAL": 22
          }
        },
        "optimal_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "lower_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "old_proposer_preference": "DIGITAL",
        "third_experience_flips_preference": true,
        "proposer_yields": true
      },
      "generation_attempts": 1,
      "form_record_ids": {
        "A": "Q067ED3F4F7",
        "B": "Q23DB5804EB"
      },
      "proposal_record_id": "Q950C0CA176",
      "confirm_record_id": "QD58F0DC692",
      "recheck_record_id": "QE64462EEED"
    },
    {
      "id": "N02",
      "proposer": "B",
      "peer": "A",
      "strength": "WEAK",
      "same_personal": true,
      "role_order": [
        "B",
        "A"
      ],
      "medium_order": [
        "DIGITAL",
        "PAPER"
      ],
      "experiences": [
        {
          "episode_id": "E34084CAFBA",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 18,
          "paper_success": 9
        },
        {
          "episode_id": "EE78174F2A9",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 15,
          "paper_success": 6
        },
        {
          "episode_id": "E0992A6ACBE",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 9,
          "paper_success": 10
        },
        {
          "episode_id": "EFD5E48A417",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 11,
          "paper_success": 7
        },
        {
          "episode_id": "EEDFFDC50FD",
          "observer": "B",
          "site": "区画2",
          "session": 3,
          "attempts_per_medium": 40,
          "digital_success": 11,
          "paper_success": 19
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "X",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 37
        },
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 39
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "DIGITAL",
          "B": "DIGITAL"
        },
        "projected_per_40": {
          "B": {
            "DIGITAL": 22,
            "PAPER": 17
          },
          "A": {
            "DIGITAL": 20,
            "PAPER": 17
          }
        },
        "optimal_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "lower_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "old_proposer_preference": "DIGITAL",
        "third_experience_flips_preference": false,
        "proposer_yields": false
      },
      "generation_attempts": 1,
      "form_record_ids": {
        "A": "Q2AEAADF263",
        "B": "QA094256214"
      },
      "proposal_record_id": "QC556AE59DD",
      "confirm_record_id": "Q72FF063C23",
      "recheck_record_id": "Q58D7835B0B"
    },
    {
      "id": "N03",
      "proposer": "A",
      "peer": "B",
      "strength": "WEAK",
      "same_personal": false,
      "role_order": [
        "A",
        "B"
      ],
      "medium_order": [
        "PAPER",
        "DIGITAL"
      ],
      "experiences": [
        {
          "episode_id": "E837D9C0A7F",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 9,
          "digital_success": 9
        },
        {
          "episode_id": "E803DE431C3",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 4,
          "digital_success": 18
        },
        {
          "episode_id": "EC1822CA588",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 17,
          "digital_success": 12
        },
        {
          "episode_id": "E4553017BC5",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 5,
          "digital_success": 11
        },
        {
          "episode_id": "E2B2525699D",
          "observer": "A",
          "site": "区画1",
          "session": 3,
          "attempts_per_medium": 40,
          "paper_success": 25,
          "digital_success": 9
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 40
        },
        {
          "candidate_id": "X",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 42
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "projected_per_40": {
          "A": {
            "PAPER": 19,
            "DIGITAL": 18
          },
          "B": {
            "DIGITAL": 23,
            "PAPER": 22
          }
        },
        "optimal_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "lower_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "old_proposer_preference": "DIGITAL",
        "third_experience_flips_preference": true,
        "proposer_yields": false
      },
      "generation_attempts": 2,
      "form_record_ids": {
        "A": "Q8DC50ABD1F",
        "B": "Q6EB2A0941C"
      },
      "proposal_record_id": "Q08D6040F05",
      "confirm_record_id": "Q28D078BEB6",
      "recheck_record_id": "QADC04BB16C"
    },
    {
      "id": "N04",
      "proposer": "B",
      "peer": "A",
      "strength": "WEAK",
      "same_personal": false,
      "role_order": [
        "B",
        "A"
      ],
      "medium_order": [
        "DIGITAL",
        "PAPER"
      ],
      "experiences": [
        {
          "episode_id": "E3B183581A6",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 8,
          "paper_success": 6
        },
        {
          "episode_id": "EB81AB667C9",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 5,
          "paper_success": 6
        },
        {
          "episode_id": "E8401940C46",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 10,
          "paper_success": 11
        },
        {
          "episode_id": "EB4F4D790F8",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 6,
          "paper_success": 6
        },
        {
          "episode_id": "E705EF7401A",
          "observer": "B",
          "site": "区画2",
          "session": 3,
          "attempts_per_medium": 40,
          "digital_success": 17,
          "paper_success": 16
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 32
        },
        {
          "candidate_id": "X",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 30
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "projected_per_40": {
          "B": {
            "DIGITAL": 15,
            "PAPER": 14
          },
          "A": {
            "PAPER": 17,
            "DIGITAL": 16
          }
        },
        "optimal_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "lower_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "old_proposer_preference": "DIGITAL",
        "third_experience_flips_preference": false,
        "proposer_yields": false
      },
      "generation_attempts": 1,
      "form_record_ids": {
        "A": "Q9016B98EA0",
        "B": "QD88E52C4FF"
      },
      "proposal_record_id": "Q3945A865E1",
      "confirm_record_id": "Q1BA3D6F1AC",
      "recheck_record_id": "QBB71388AD2"
    },
    {
      "id": "N05",
      "proposer": "A",
      "peer": "B",
      "strength": "STRONG",
      "same_personal": true,
      "role_order": [
        "A",
        "B"
      ],
      "medium_order": [
        "PAPER",
        "DIGITAL"
      ],
      "experiences": [
        {
          "episode_id": "EC35E47448B",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 5,
          "digital_success": 5
        },
        {
          "episode_id": "EB4316EB4AA",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 18,
          "digital_success": 7
        },
        {
          "episode_id": "EBCA7CF3A61",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 7,
          "digital_success": 4
        },
        {
          "episode_id": "E5B9820C89A",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 8,
          "digital_success": 13
        },
        {
          "episode_id": "EA2C8D25663",
          "observer": "A",
          "site": "区画1",
          "session": 3,
          "attempts_per_medium": 40,
          "paper_success": 5,
          "digital_success": 36
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "X",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 39
        },
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 31
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "DIGITAL",
          "B": "DIGITAL"
        },
        "projected_per_40": {
          "A": {
            "DIGITAL": 24,
            "PAPER": 14
          },
          "B": {
            "DIGITAL": 17,
            "PAPER": 15
          }
        },
        "optimal_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "lower_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "old_proposer_preference": "PAPER",
        "third_experience_flips_preference": true,
        "proposer_yields": false
      },
      "generation_attempts": 6,
      "form_record_ids": {
        "A": "Q7E1AA75DB0",
        "B": "Q6DF586CEBE"
      },
      "proposal_record_id": "Q4A67A15B6A",
      "confirm_record_id": "Q906DCEFF8B",
      "recheck_record_id": "Q00C8513B78"
    },
    {
      "id": "N06",
      "proposer": "B",
      "peer": "A",
      "strength": "STRONG",
      "same_personal": true,
      "role_order": [
        "B",
        "A"
      ],
      "medium_order": [
        "DIGITAL",
        "PAPER"
      ],
      "experiences": [
        {
          "episode_id": "ED6B23BC078",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 9,
          "paper_success": 16
        },
        {
          "episode_id": "E910ABE75BA",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 12,
          "paper_success": 14
        },
        {
          "episode_id": "E6A98F1EAD0",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 14,
          "paper_success": 18
        },
        {
          "episode_id": "E348E325450",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 8,
          "paper_success": 14
        },
        {
          "episode_id": "E36B2003854",
          "observer": "B",
          "site": "区画2",
          "session": 3,
          "attempts_per_medium": 40,
          "digital_success": 23,
          "paper_success": 18
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "X",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 54
        },
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 46
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "PAPER",
          "B": "PAPER"
        },
        "projected_per_40": {
          "B": {
            "PAPER": 24,
            "DIGITAL": 22
          },
          "A": {
            "PAPER": 32,
            "DIGITAL": 22
          }
        },
        "optimal_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "lower_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "old_proposer_preference": "PAPER",
        "third_experience_flips_preference": false,
        "proposer_yields": true
      },
      "generation_attempts": 5,
      "form_record_ids": {
        "A": "QAE905C971B",
        "B": "Q8411094FF9"
      },
      "proposal_record_id": "Q9635AB88D7",
      "confirm_record_id": "QDB5CB33CDE",
      "recheck_record_id": "Q5960FC0D7D"
    },
    {
      "id": "N07",
      "proposer": "A",
      "peer": "B",
      "strength": "STRONG",
      "same_personal": false,
      "role_order": [
        "A",
        "B"
      ],
      "medium_order": [
        "PAPER",
        "DIGITAL"
      ],
      "experiences": [
        {
          "episode_id": "E6826FE843C",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 18,
          "digital_success": 5
        },
        {
          "episode_id": "E26133C5DCB",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 5,
          "digital_success": 6
        },
        {
          "episode_id": "E2CFD3987D9",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "paper_success": 11,
          "digital_success": 14
        },
        {
          "episode_id": "E33BB0AC4A2",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "paper_success": 18,
          "digital_success": 10
        },
        {
          "episode_id": "E30F15E07DE",
          "observer": "A",
          "site": "区画1",
          "session": 3,
          "attempts_per_medium": 40,
          "paper_success": 11,
          "digital_success": 29
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 41
        },
        {
          "candidate_id": "X",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 49
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "projected_per_40": {
          "A": {
            "DIGITAL": 20,
            "PAPER": 17
          },
          "B": {
            "PAPER": 29,
            "DIGITAL": 24
          }
        },
        "optimal_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "lower_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "old_proposer_preference": "PAPER",
        "third_experience_flips_preference": true,
        "proposer_yields": false
      },
      "generation_attempts": 3,
      "form_record_ids": {
        "A": "Q46D7720177",
        "B": "QB4015FA589"
      },
      "proposal_record_id": "Q851D44FC12",
      "confirm_record_id": "Q7452A8E42D",
      "recheck_record_id": "Q3496C1723A"
    },
    {
      "id": "N08",
      "proposer": "B",
      "peer": "A",
      "strength": "STRONG",
      "same_personal": false,
      "role_order": [
        "B",
        "A"
      ],
      "medium_order": [
        "DIGITAL",
        "PAPER"
      ],
      "experiences": [
        {
          "episode_id": "E787FED353C",
          "observer": "B",
          "site": "区画2",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 5,
          "paper_success": 18
        },
        {
          "episode_id": "E5ED4D0A13A",
          "observer": "B",
          "site": "区画2",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 5,
          "paper_success": 12
        },
        {
          "episode_id": "EE5B2283C3D",
          "observer": "A",
          "site": "区画1",
          "session": 1,
          "attempts_per_medium": 20,
          "digital_success": 9,
          "paper_success": 8
        },
        {
          "episode_id": "EBA722BAC5F",
          "observer": "A",
          "site": "区画1",
          "session": 2,
          "attempts_per_medium": 20,
          "digital_success": 11,
          "paper_success": 7
        },
        {
          "episode_id": "EB78F6CD72E",
          "observer": "B",
          "site": "区画2",
          "session": 3,
          "attempts_per_medium": 40,
          "digital_success": 36,
          "paper_success": 22
        }
      ],
      "joint_candidate_totals": [
        {
          "candidate_id": "Y",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "projected_total_success_per_40_each": 46
        },
        {
          "candidate_id": "X",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "projected_total_success_per_40_each": 38
        }
      ],
      "reference_not_for_model": {
        "local": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "projected_per_40": {
          "B": {
            "PAPER": 26,
            "DIGITAL": 23
          },
          "A": {
            "DIGITAL": 20,
            "PAPER": 15
          }
        },
        "optimal_allocation": {
          "A": "DIGITAL",
          "B": "PAPER"
        },
        "lower_allocation": {
          "A": "PAPER",
          "B": "DIGITAL"
        },
        "old_proposer_preference": "PAPER",
        "third_experience_flips_preference": false,
        "proposer_yields": false
      },
      "generation_attempts": 3,
      "form_record_ids": {
        "A": "QDEA60100C3",
        "B": "QAB11020B7D"
      },
      "proposal_record_id": "Q7A1F084817",
      "confirm_record_id": "Q650A8F11D7",
      "recheck_record_id": "Q488E8F1C51"
    }
  ],
  "condition_order_by_case": {
    "N01": [
      "EARLY",
      "LATE"
    ],
    "N02": [
      "LATE",
      "EARLY"
    ],
    "N03": [
      "LATE",
      "EARLY"
    ],
    "N04": [
      "EARLY",
      "LATE"
    ],
    "N05": [
      "LATE",
      "EARLY"
    ],
    "N06": [
      "EARLY",
      "LATE"
    ],
    "N07": [
      "EARLY",
      "LATE"
    ],
    "N08": [
      "LATE",
      "EARLY"
    ]
  },
  "paths": [
    {
      "id": "ST01-EARLY-N07-OPTIMAL",
      "case": "N07",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N07-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N07-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N07-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N07-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-OPTIMAL",
      "case": "N07",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N07-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N07-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N07-OPTIMAL-USE-A",
        "B": "ST01-LATE-N07-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N07-LOWER",
      "case": "N07",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N07-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N07-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N07-LOWER-USE-A",
        "B": "ST01-EARLY-N07-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-LOWER",
      "case": "N07",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N07-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N07-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N07-LOWER-USE-A",
        "B": "ST01-LATE-N07-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N07-DUPLICATE",
      "case": "N07",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N07-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N07-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N07-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N07-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-DUPLICATE",
      "case": "N07",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q851D44FC12",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E6826FE843C",
            "E26133C5DCB",
            "E2CFD3987D9",
            "E33BB0AC4A2",
            "E30F15E07DE"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N07-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N07-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N07-DUPLICATE-USE-A",
        "B": "ST01-LATE-N07-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-OPTIMAL",
      "case": "N04",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N04-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N04-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N04-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N04-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-OPTIMAL",
      "case": "N04",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N04-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N04-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N04-OPTIMAL-USE-A",
        "B": "ST01-LATE-N04-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DUPLICATE",
      "case": "N04",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N04-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N04-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N04-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N04-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DUPLICATE",
      "case": "N04",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N04-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N04-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N04-DUPLICATE-USE-A",
        "B": "ST01-LATE-N04-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-LOWER",
      "case": "N04",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N04-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N04-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N04-LOWER-USE-A",
        "B": "ST01-EARLY-N04-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-LOWER",
      "case": "N04",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N04-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N04-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N04-LOWER-USE-A",
        "B": "ST01-LATE-N04-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-LOWER",
      "case": "N05",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N05-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N05-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N05-LOWER-USE-A",
        "B": "ST01-LATE-N05-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-LOWER",
      "case": "N05",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N05-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N05-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N05-LOWER-USE-A",
        "B": "ST01-EARLY-N05-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-OPTIMAL",
      "case": "N05",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N05-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N05-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N05-OPTIMAL-USE-A",
        "B": "ST01-LATE-N05-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-OPTIMAL",
      "case": "N05",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N05-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N05-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N05-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N05-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DUPLICATE",
      "case": "N05",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N05-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N05-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N05-DUPLICATE-USE-A",
        "B": "ST01-LATE-N05-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DUPLICATE",
      "case": "N05",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N05-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N05-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N05-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N05-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-LOWER",
      "case": "N06",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N06-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N06-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N06-LOWER-USE-A",
        "B": "ST01-EARLY-N06-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-LOWER",
      "case": "N06",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N06-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N06-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N06-LOWER-USE-A",
        "B": "ST01-LATE-N06-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-DUPLICATE",
      "case": "N06",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N06-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N06-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N06-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N06-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-DUPLICATE",
      "case": "N06",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N06-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N06-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N06-DUPLICATE-USE-A",
        "B": "ST01-LATE-N06-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-OPTIMAL",
      "case": "N06",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N06-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N06-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N06-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N06-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-OPTIMAL",
      "case": "N06",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q9635AB88D7",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED6B23BC078",
            "E910ABE75BA",
            "E6A98F1EAD0",
            "E348E325450",
            "E36B2003854"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N06-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N06-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N06-OPTIMAL-USE-A",
        "B": "ST01-LATE-N06-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-DUPLICATE",
      "case": "N02",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N02-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N02-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N02-DUPLICATE-USE-A",
        "B": "ST01-LATE-N02-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-DUPLICATE",
      "case": "N02",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N02-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N02-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N02-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N02-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N02-OPTIMAL",
      "case": "N02",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N02-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N02-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N02-OPTIMAL-USE-A",
        "B": "ST01-LATE-N02-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-OPTIMAL",
      "case": "N02",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N02-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N02-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N02-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N02-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N02-LOWER",
      "case": "N02",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N02-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N02-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N02-LOWER-USE-A",
        "B": "ST01-LATE-N02-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-LOWER",
      "case": "N02",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "QC556AE59DD",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E34084CAFBA",
            "EE78174F2A9",
            "E0992A6ACBE",
            "EFD5E48A417",
            "EEDFFDC50FD"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N02-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N02-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N02-LOWER-USE-A",
        "B": "ST01-EARLY-N02-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-DUPLICATE",
      "case": "N03",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N03-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N03-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N03-DUPLICATE-USE-A",
        "B": "ST01-LATE-N03-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-DUPLICATE",
      "case": "N03",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N03-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N03-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N03-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N03-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-LOWER",
      "case": "N03",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N03-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N03-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N03-LOWER-USE-A",
        "B": "ST01-LATE-N03-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-LOWER",
      "case": "N03",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N03-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N03-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N03-LOWER-USE-A",
        "B": "ST01-EARLY-N03-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-OPTIMAL",
      "case": "N03",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N03-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N03-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N03-OPTIMAL-USE-A",
        "B": "ST01-LATE-N03-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-OPTIMAL",
      "case": "N03",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q08D6040F05",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E837D9C0A7F",
            "E803DE431C3",
            "EC1822CA588",
            "E4553017BC5",
            "E2B2525699D"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N03-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N03-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N03-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N03-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-OPTIMAL",
      "case": "N01",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N01-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N01-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N01-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N01-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-OPTIMAL",
      "case": "N01",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N01-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N01-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N01-OPTIMAL-USE-A",
        "B": "ST01-LATE-N01-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-LOWER",
      "case": "N01",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N01-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N01-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N01-LOWER-USE-A",
        "B": "ST01-EARLY-N01-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-LOWER",
      "case": "N01",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N01-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N01-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N01-LOWER-USE-A",
        "B": "ST01-LATE-N01-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DUPLICATE",
      "case": "N01",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N01-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N01-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N01-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N01-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DUPLICATE",
      "case": "N01",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N01-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N01-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N01-DUPLICATE-USE-A",
        "B": "ST01-LATE-N01-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-LOWER",
      "case": "N08",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N08-LOWER-CONFIRM",
      "recheck_id": "ST01-LATE-N08-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N08-LOWER-USE-A",
        "B": "ST01-LATE-N08-LOWER-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-LOWER",
      "case": "N08",
      "initial_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N08-LOWER-CONFIRM",
      "recheck_id": "ST01-EARLY-N08-LOWER-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N08-LOWER-USE-A",
        "B": "ST01-EARLY-N08-LOWER-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DUPLICATE",
      "case": "N08",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N08-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-LATE-N08-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N08-DUPLICATE-USE-A",
        "B": "ST01-LATE-N08-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DUPLICATE",
      "case": "N08",
      "initial_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N08-DUPLICATE-CONFIRM",
      "recheck_id": "ST01-EARLY-N08-DUPLICATE-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N08-DUPLICATE-USE-A",
        "B": "ST01-EARLY-N08-DUPLICATE-USE-B"
      },
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-OPTIMAL",
      "case": "N08",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "confirm_id": "ST01-LATE-N08-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-LATE-N08-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-LATE-N08-OPTIMAL-USE-A",
        "B": "ST01-LATE-N08-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-OPTIMAL",
      "case": "N08",
      "initial_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "form_ids": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "confirm_id": "ST01-EARLY-N08-OPTIMAL-CONFIRM",
      "recheck_id": "ST01-EARLY-N08-OPTIMAL-RECHECK",
      "use_ids": {
        "A": "ST01-EARLY-N08-OPTIMAL-USE-A",
        "B": "ST01-EARLY-N08-OPTIMAL-USE-B"
      },
      "condition_not_for_model": "EARLY"
    }
  ],
  "paired_paths": [
    {
      "id": "N07-OPTIMAL",
      "case": "N07",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N07-OPTIMAL",
        "EARLY": "ST01-EARLY-N07-OPTIMAL"
      }
    },
    {
      "id": "N07-LOWER",
      "case": "N07",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N07-LOWER",
        "EARLY": "ST01-EARLY-N07-LOWER"
      }
    },
    {
      "id": "N07-DUPLICATE",
      "case": "N07",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N07-DUPLICATE",
        "EARLY": "ST01-EARLY-N07-DUPLICATE"
      }
    },
    {
      "id": "N04-OPTIMAL",
      "case": "N04",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N04-OPTIMAL",
        "EARLY": "ST01-EARLY-N04-OPTIMAL"
      }
    },
    {
      "id": "N04-DUPLICATE",
      "case": "N04",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N04-DUPLICATE",
        "EARLY": "ST01-EARLY-N04-DUPLICATE"
      }
    },
    {
      "id": "N04-LOWER",
      "case": "N04",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N04-LOWER",
        "EARLY": "ST01-EARLY-N04-LOWER"
      }
    },
    {
      "id": "N05-LOWER",
      "case": "N05",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N05-LOWER",
        "EARLY": "ST01-EARLY-N05-LOWER"
      }
    },
    {
      "id": "N05-OPTIMAL",
      "case": "N05",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N05-OPTIMAL",
        "EARLY": "ST01-EARLY-N05-OPTIMAL"
      }
    },
    {
      "id": "N05-DUPLICATE",
      "case": "N05",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N05-DUPLICATE",
        "EARLY": "ST01-EARLY-N05-DUPLICATE"
      }
    },
    {
      "id": "N06-LOWER",
      "case": "N06",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N06-LOWER",
        "EARLY": "ST01-EARLY-N06-LOWER"
      }
    },
    {
      "id": "N06-DUPLICATE",
      "case": "N06",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N06-DUPLICATE",
        "EARLY": "ST01-EARLY-N06-DUPLICATE"
      }
    },
    {
      "id": "N06-OPTIMAL",
      "case": "N06",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N06-OPTIMAL",
        "EARLY": "ST01-EARLY-N06-OPTIMAL"
      }
    },
    {
      "id": "N02-DUPLICATE",
      "case": "N02",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N02-DUPLICATE",
        "EARLY": "ST01-EARLY-N02-DUPLICATE"
      }
    },
    {
      "id": "N02-OPTIMAL",
      "case": "N02",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N02-OPTIMAL",
        "EARLY": "ST01-EARLY-N02-OPTIMAL"
      }
    },
    {
      "id": "N02-LOWER",
      "case": "N02",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N02-LOWER",
        "EARLY": "ST01-EARLY-N02-LOWER"
      }
    },
    {
      "id": "N03-DUPLICATE",
      "case": "N03",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N03-DUPLICATE",
        "EARLY": "ST01-EARLY-N03-DUPLICATE"
      }
    },
    {
      "id": "N03-LOWER",
      "case": "N03",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N03-LOWER",
        "EARLY": "ST01-EARLY-N03-LOWER"
      }
    },
    {
      "id": "N03-OPTIMAL",
      "case": "N03",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N03-OPTIMAL",
        "EARLY": "ST01-EARLY-N03-OPTIMAL"
      }
    },
    {
      "id": "N01-OPTIMAL",
      "case": "N01",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N01-OPTIMAL",
        "EARLY": "ST01-EARLY-N01-OPTIMAL"
      }
    },
    {
      "id": "N01-LOWER",
      "case": "N01",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N01-LOWER",
        "EARLY": "ST01-EARLY-N01-LOWER"
      }
    },
    {
      "id": "N01-DUPLICATE",
      "case": "N01",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N01-DUPLICATE",
        "EARLY": "ST01-EARLY-N01-DUPLICATE"
      }
    },
    {
      "id": "N08-LOWER",
      "case": "N08",
      "initial_type": "LOWER",
      "paths": {
        "LATE": "ST01-LATE-N08-LOWER",
        "EARLY": "ST01-EARLY-N08-LOWER"
      }
    },
    {
      "id": "N08-DUPLICATE",
      "case": "N08",
      "initial_type": "DUPLICATE",
      "paths": {
        "LATE": "ST01-LATE-N08-DUPLICATE",
        "EARLY": "ST01-EARLY-N08-DUPLICATE"
      }
    },
    {
      "id": "N08-OPTIMAL",
      "case": "N08",
      "initial_type": "OPTIMAL",
      "paths": {
        "LATE": "ST01-LATE-N08-OPTIMAL",
        "EARLY": "ST01-EARLY-N08-OPTIMAL"
      }
    }
  ],
  "diagnostics": [
    {
      "id": "ST01-EARLY-N01-DIAG-LOWER",
      "case": "N01",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-LOWER",
      "case": "N01",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DIAG-OPTIMAL",
      "case": "N01",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-OPTIMAL",
      "case": "N01",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DIAG-DUPLICATE",
      "case": "N01",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-DUPLICATE",
      "case": "N01",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q950C0CA176",
        "author": "A",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "Q41E1275B06",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q950C0CA176",
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "ED81AAE200D",
            "EFB9B239791",
            "E5A03A1A255",
            "E6A5E6E3A8F",
            "E22BFDC1C77"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-OPTIMAL",
      "case": "N04",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-OPTIMAL",
      "case": "N04",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-DUPLICATE",
      "case": "N04",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-DUPLICATE",
      "case": "N04",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-LOWER",
      "case": "N04",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-LOWER",
      "case": "N04",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q3945A865E1",
        "author": "B",
        "body": {
          "allocation": {
            "A": "PAPER",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QA20CE4E012",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q3945A865E1",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E3B183581A6",
            "EB81AB667C9",
            "E8401940C46",
            "EB4F4D790F8",
            "E705EF7401A"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-DIAG-DUPLICATE",
      "case": "N08",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-DUPLICATE",
      "case": "N08",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DIAG-LOWER",
      "case": "N08",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-LOWER",
      "case": "N08",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DIAG-OPTIMAL",
      "case": "N08",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-OPTIMAL",
      "case": "N08",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q7A1F084817",
        "author": "B",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "counter_record": {
        "author": "A",
        "record_id": "QE45F2257AE",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q7A1F084817",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "E787FED353C",
            "E5ED4D0A13A",
            "EE5B2283C3D",
            "EBA722BAC5F",
            "EB78F6CD72E"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-LOWER",
      "case": "N05",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-LOWER",
      "case": "N05",
      "counter_type_not_for_model": "LOWER",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "PAPER",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-OPTIMAL",
      "case": "N05",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-OPTIMAL",
      "case": "N05",
      "counter_type_not_for_model": "OPTIMAL",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "DIGITAL",
            "B": "PAPER"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "ACCEPT",
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-DUPLICATE",
      "case": "N05",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-DUPLICATE",
      "case": "N05",
      "counter_type_not_for_model": "DUPLICATE",
      "initial_proposal": {
        "record_id": "Q4A67A15B6A",
        "author": "A",
        "body": {
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "counter_record": {
        "author": "B",
        "record_id": "QAA9DF10342",
        "body": {
          "action": "COUNTER",
          "reply_to": "Q4A67A15B6A",
          "allocation": {
            "A": "DIGITAL",
            "B": "DIGITAL"
          },
          "evidence_refs": [
            "EC35E47448B",
            "EB4316EB4AA",
            "EBCA7CF3A61",
            "E5B9820C89A",
            "EA2C8D25663"
          ]
        }
      },
      "expected_action_not_for_model": "HOLD",
      "condition_not_for_model": "EARLY"
    }
  ],
  "paired_diagnostics": [
    {
      "id": "N01-DIAG-LOWER",
      "case": "N01",
      "counter_type": "LOWER",
      "diagnostics": {
        "LATE": "ST01-LATE-N01-DIAG-LOWER",
        "EARLY": "ST01-EARLY-N01-DIAG-LOWER"
      }
    },
    {
      "id": "N01-DIAG-OPTIMAL",
      "case": "N01",
      "counter_type": "OPTIMAL",
      "diagnostics": {
        "LATE": "ST01-LATE-N01-DIAG-OPTIMAL",
        "EARLY": "ST01-EARLY-N01-DIAG-OPTIMAL"
      }
    },
    {
      "id": "N01-DIAG-DUPLICATE",
      "case": "N01",
      "counter_type": "DUPLICATE",
      "diagnostics": {
        "LATE": "ST01-LATE-N01-DIAG-DUPLICATE",
        "EARLY": "ST01-EARLY-N01-DIAG-DUPLICATE"
      }
    },
    {
      "id": "N04-DIAG-OPTIMAL",
      "case": "N04",
      "counter_type": "OPTIMAL",
      "diagnostics": {
        "LATE": "ST01-LATE-N04-DIAG-OPTIMAL",
        "EARLY": "ST01-EARLY-N04-DIAG-OPTIMAL"
      }
    },
    {
      "id": "N04-DIAG-DUPLICATE",
      "case": "N04",
      "counter_type": "DUPLICATE",
      "diagnostics": {
        "LATE": "ST01-LATE-N04-DIAG-DUPLICATE",
        "EARLY": "ST01-EARLY-N04-DIAG-DUPLICATE"
      }
    },
    {
      "id": "N04-DIAG-LOWER",
      "case": "N04",
      "counter_type": "LOWER",
      "diagnostics": {
        "LATE": "ST01-LATE-N04-DIAG-LOWER",
        "EARLY": "ST01-EARLY-N04-DIAG-LOWER"
      }
    },
    {
      "id": "N08-DIAG-DUPLICATE",
      "case": "N08",
      "counter_type": "DUPLICATE",
      "diagnostics": {
        "LATE": "ST01-LATE-N08-DIAG-DUPLICATE",
        "EARLY": "ST01-EARLY-N08-DIAG-DUPLICATE"
      }
    },
    {
      "id": "N08-DIAG-LOWER",
      "case": "N08",
      "counter_type": "LOWER",
      "diagnostics": {
        "LATE": "ST01-LATE-N08-DIAG-LOWER",
        "EARLY": "ST01-EARLY-N08-DIAG-LOWER"
      }
    },
    {
      "id": "N08-DIAG-OPTIMAL",
      "case": "N08",
      "counter_type": "OPTIMAL",
      "diagnostics": {
        "LATE": "ST01-LATE-N08-DIAG-OPTIMAL",
        "EARLY": "ST01-EARLY-N08-DIAG-OPTIMAL"
      }
    },
    {
      "id": "N05-DIAG-LOWER",
      "case": "N05",
      "counter_type": "LOWER",
      "diagnostics": {
        "LATE": "ST01-LATE-N05-DIAG-LOWER",
        "EARLY": "ST01-EARLY-N05-DIAG-LOWER"
      }
    },
    {
      "id": "N05-DIAG-OPTIMAL",
      "case": "N05",
      "counter_type": "OPTIMAL",
      "diagnostics": {
        "LATE": "ST01-LATE-N05-DIAG-OPTIMAL",
        "EARLY": "ST01-EARLY-N05-DIAG-OPTIMAL"
      }
    },
    {
      "id": "N05-DIAG-DUPLICATE",
      "case": "N05",
      "counter_type": "DUPLICATE",
      "diagnostics": {
        "LATE": "ST01-LATE-N05-DIAG-DUPLICATE",
        "EARLY": "ST01-EARLY-N05-DIAG-DUPLICATE"
      }
    }
  ],
  "allocation": [
    {
      "id": "ST01-EARLY-N07-FORM-A",
      "case": "N07",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1557132674,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-FORM-A",
      "case": "N07",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1557132674,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N07-FORM-B",
      "case": "N07",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 114477581,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-FORM-B",
      "case": "N07",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 114477581,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-FORM-B",
      "case": "N04",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 2054213850,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-FORM-B",
      "case": "N04",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 2054213850,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-FORM-A",
      "case": "N04",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1658813601,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-FORM-A",
      "case": "N04",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1658813601,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-FORM-B",
      "case": "N08",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1110848564,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-FORM-B",
      "case": "N08",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1110848564,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-FORM-A",
      "case": "N08",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 501341389,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-FORM-A",
      "case": "N08",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 501341389,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-FORM-A",
      "case": "N05",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 886346083,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-FORM-A",
      "case": "N05",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 886346083,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-FORM-B",
      "case": "N05",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 693254905,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-FORM-B",
      "case": "N05",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 693254905,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-FORM-A",
      "case": "N01",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 2026573670,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-FORM-A",
      "case": "N01",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 2026573670,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-FORM-B",
      "case": "N01",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 2023086990,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-FORM-B",
      "case": "N01",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 2023086990,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-FORM-B",
      "case": "N06",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1984451973,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-FORM-B",
      "case": "N06",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1984451973,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-FORM-A",
      "case": "N06",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 202712062,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-FORM-A",
      "case": "N06",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 202712062,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-FORM-B",
      "case": "N02",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1534377168,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-FORM-B",
      "case": "N02",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 1534377168,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N02-FORM-A",
      "case": "N02",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1839561640,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-FORM-A",
      "case": "N02",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1839561640,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-FORM-A",
      "case": "N03",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1625931029,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-FORM-A",
      "case": "N03",
      "role": "A",
      "stage": "FORM",
      "parents": [],
      "seed": 1625931029,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-FORM-B",
      "case": "N03",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 46159877,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-FORM-B",
      "case": "N03",
      "role": "B",
      "stage": "FORM",
      "parents": [],
      "seed": 46159877,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-OPTIMAL-CONFIRM",
      "case": "N07",
      "route": "ST01-EARLY-N07-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-OPTIMAL-RECHECK",
      "case": "N07",
      "route": "ST01-EARLY-N07-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-OPTIMAL-USE-A",
      "case": "N07",
      "route": "ST01-EARLY-N07-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-OPTIMAL-CONFIRM",
        "ST01-EARLY-N07-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-OPTIMAL-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-OPTIMAL-USE-B",
      "case": "N07",
      "route": "ST01-EARLY-N07-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-OPTIMAL-CONFIRM",
        "ST01-EARLY-N07-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-OPTIMAL-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-OPTIMAL-CONFIRM",
      "case": "N07",
      "route": "ST01-LATE-N07-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-OPTIMAL-RECHECK",
      "case": "N07",
      "route": "ST01-LATE-N07-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-OPTIMAL-USE-A",
      "case": "N07",
      "route": "ST01-LATE-N07-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-OPTIMAL-CONFIRM",
        "ST01-LATE-N07-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-OPTIMAL-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-OPTIMAL-USE-B",
      "case": "N07",
      "route": "ST01-LATE-N07-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-OPTIMAL-CONFIRM",
        "ST01-LATE-N07-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-OPTIMAL-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N07-LOWER-CONFIRM",
      "case": "N07",
      "route": "ST01-EARLY-N07-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-LOWER-RECHECK",
      "case": "N07",
      "route": "ST01-EARLY-N07-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-LOWER-USE-A",
      "case": "N07",
      "route": "ST01-EARLY-N07-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-LOWER-CONFIRM",
        "ST01-EARLY-N07-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-LOWER-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-LOWER-USE-B",
      "case": "N07",
      "route": "ST01-EARLY-N07-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-LOWER-CONFIRM",
        "ST01-EARLY-N07-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-LOWER-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-LOWER-CONFIRM",
      "case": "N07",
      "route": "ST01-LATE-N07-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-LOWER-RECHECK",
      "case": "N07",
      "route": "ST01-LATE-N07-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-LOWER-USE-A",
      "case": "N07",
      "route": "ST01-LATE-N07-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-LOWER-CONFIRM",
        "ST01-LATE-N07-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-LOWER-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-LOWER-USE-B",
      "case": "N07",
      "route": "ST01-LATE-N07-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-LOWER-CONFIRM",
        "ST01-LATE-N07-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-LOWER-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N07-DUPLICATE-CONFIRM",
      "case": "N07",
      "route": "ST01-EARLY-N07-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-DUPLICATE-RECHECK",
      "case": "N07",
      "route": "ST01-EARLY-N07-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-DUPLICATE-USE-A",
      "case": "N07",
      "route": "ST01-EARLY-N07-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-DUPLICATE-CONFIRM",
        "ST01-EARLY-N07-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-DUPLICATE-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N07-DUPLICATE-USE-B",
      "case": "N07",
      "route": "ST01-EARLY-N07-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N07-FORM-A",
        "ST01-EARLY-N07-FORM-B",
        "ST01-EARLY-N07-DUPLICATE-CONFIRM",
        "ST01-EARLY-N07-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N07-DUPLICATE-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N07-DUPLICATE-CONFIRM",
      "case": "N07",
      "route": "ST01-LATE-N07-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B"
      ],
      "seed": 1418164781,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-DUPLICATE-RECHECK",
      "case": "N07",
      "route": "ST01-LATE-N07-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2101349371,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-DUPLICATE-USE-A",
      "case": "N07",
      "route": "ST01-LATE-N07-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-DUPLICATE-CONFIRM",
        "ST01-LATE-N07-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-DUPLICATE-RECHECK",
      "seed": 562964867,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N07-DUPLICATE-USE-B",
      "case": "N07",
      "route": "ST01-LATE-N07-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N07-FORM-A",
        "ST01-LATE-N07-FORM-B",
        "ST01-LATE-N07-DUPLICATE-CONFIRM",
        "ST01-LATE-N07-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N07-DUPLICATE-RECHECK",
      "seed": 754747542,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-OPTIMAL-CONFIRM",
      "case": "N04",
      "route": "ST01-EARLY-N04-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-OPTIMAL-RECHECK",
      "case": "N04",
      "route": "ST01-EARLY-N04-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-OPTIMAL-USE-B",
      "case": "N04",
      "route": "ST01-EARLY-N04-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-OPTIMAL-CONFIRM",
        "ST01-EARLY-N04-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-OPTIMAL-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-OPTIMAL-USE-A",
      "case": "N04",
      "route": "ST01-EARLY-N04-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-OPTIMAL-CONFIRM",
        "ST01-EARLY-N04-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-OPTIMAL-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-OPTIMAL-CONFIRM",
      "case": "N04",
      "route": "ST01-LATE-N04-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-OPTIMAL-RECHECK",
      "case": "N04",
      "route": "ST01-LATE-N04-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-OPTIMAL-USE-B",
      "case": "N04",
      "route": "ST01-LATE-N04-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-OPTIMAL-CONFIRM",
        "ST01-LATE-N04-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-OPTIMAL-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-OPTIMAL-USE-A",
      "case": "N04",
      "route": "ST01-LATE-N04-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-OPTIMAL-CONFIRM",
        "ST01-LATE-N04-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-OPTIMAL-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DUPLICATE-CONFIRM",
      "case": "N04",
      "route": "ST01-EARLY-N04-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-DUPLICATE-RECHECK",
      "case": "N04",
      "route": "ST01-EARLY-N04-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-DUPLICATE-USE-B",
      "case": "N04",
      "route": "ST01-EARLY-N04-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-DUPLICATE-CONFIRM",
        "ST01-EARLY-N04-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-DUPLICATE-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-DUPLICATE-USE-A",
      "case": "N04",
      "route": "ST01-EARLY-N04-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-DUPLICATE-CONFIRM",
        "ST01-EARLY-N04-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-DUPLICATE-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DUPLICATE-CONFIRM",
      "case": "N04",
      "route": "ST01-LATE-N04-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-DUPLICATE-RECHECK",
      "case": "N04",
      "route": "ST01-LATE-N04-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-DUPLICATE-USE-B",
      "case": "N04",
      "route": "ST01-LATE-N04-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-DUPLICATE-CONFIRM",
        "ST01-LATE-N04-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-DUPLICATE-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-DUPLICATE-USE-A",
      "case": "N04",
      "route": "ST01-LATE-N04-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-DUPLICATE-CONFIRM",
        "ST01-LATE-N04-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-DUPLICATE-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-LOWER-CONFIRM",
      "case": "N04",
      "route": "ST01-EARLY-N04-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-LOWER-RECHECK",
      "case": "N04",
      "route": "ST01-EARLY-N04-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-LOWER-USE-B",
      "case": "N04",
      "route": "ST01-EARLY-N04-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-LOWER-CONFIRM",
        "ST01-EARLY-N04-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-LOWER-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N04-LOWER-USE-A",
      "case": "N04",
      "route": "ST01-EARLY-N04-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N04-FORM-A",
        "ST01-EARLY-N04-FORM-B",
        "ST01-EARLY-N04-LOWER-CONFIRM",
        "ST01-EARLY-N04-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N04-LOWER-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-LOWER-CONFIRM",
      "case": "N04",
      "route": "ST01-LATE-N04-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1950277104,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-LOWER-RECHECK",
      "case": "N04",
      "route": "ST01-LATE-N04-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1064194699,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-LOWER-USE-B",
      "case": "N04",
      "route": "ST01-LATE-N04-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-LOWER-CONFIRM",
        "ST01-LATE-N04-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-LOWER-RECHECK",
      "seed": 645124573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N04-LOWER-USE-A",
      "case": "N04",
      "route": "ST01-LATE-N04-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N04-FORM-A",
        "ST01-LATE-N04-FORM-B",
        "ST01-LATE-N04-LOWER-CONFIRM",
        "ST01-LATE-N04-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N04-LOWER-RECHECK",
      "seed": 1518600386,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-LOWER-CONFIRM",
      "case": "N05",
      "route": "ST01-LATE-N05-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-LOWER-RECHECK",
      "case": "N05",
      "route": "ST01-LATE-N05-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-LOWER-USE-A",
      "case": "N05",
      "route": "ST01-LATE-N05-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-LOWER-CONFIRM",
        "ST01-LATE-N05-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-LOWER-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-LOWER-USE-B",
      "case": "N05",
      "route": "ST01-LATE-N05-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-LOWER-CONFIRM",
        "ST01-LATE-N05-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-LOWER-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-LOWER-CONFIRM",
      "case": "N05",
      "route": "ST01-EARLY-N05-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-LOWER-RECHECK",
      "case": "N05",
      "route": "ST01-EARLY-N05-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-LOWER-USE-A",
      "case": "N05",
      "route": "ST01-EARLY-N05-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-LOWER-CONFIRM",
        "ST01-EARLY-N05-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-LOWER-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-LOWER-USE-B",
      "case": "N05",
      "route": "ST01-EARLY-N05-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-LOWER-CONFIRM",
        "ST01-EARLY-N05-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-LOWER-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-OPTIMAL-CONFIRM",
      "case": "N05",
      "route": "ST01-LATE-N05-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-OPTIMAL-RECHECK",
      "case": "N05",
      "route": "ST01-LATE-N05-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-OPTIMAL-USE-A",
      "case": "N05",
      "route": "ST01-LATE-N05-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-OPTIMAL-CONFIRM",
        "ST01-LATE-N05-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-OPTIMAL-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-OPTIMAL-USE-B",
      "case": "N05",
      "route": "ST01-LATE-N05-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-OPTIMAL-CONFIRM",
        "ST01-LATE-N05-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-OPTIMAL-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-OPTIMAL-CONFIRM",
      "case": "N05",
      "route": "ST01-EARLY-N05-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-OPTIMAL-RECHECK",
      "case": "N05",
      "route": "ST01-EARLY-N05-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-OPTIMAL-USE-A",
      "case": "N05",
      "route": "ST01-EARLY-N05-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-OPTIMAL-CONFIRM",
        "ST01-EARLY-N05-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-OPTIMAL-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-OPTIMAL-USE-B",
      "case": "N05",
      "route": "ST01-EARLY-N05-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-OPTIMAL-CONFIRM",
        "ST01-EARLY-N05-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-OPTIMAL-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DUPLICATE-CONFIRM",
      "case": "N05",
      "route": "ST01-LATE-N05-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-DUPLICATE-RECHECK",
      "case": "N05",
      "route": "ST01-LATE-N05-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-DUPLICATE-USE-A",
      "case": "N05",
      "route": "ST01-LATE-N05-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-DUPLICATE-CONFIRM",
        "ST01-LATE-N05-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-DUPLICATE-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N05-DUPLICATE-USE-B",
      "case": "N05",
      "route": "ST01-LATE-N05-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N05-FORM-A",
        "ST01-LATE-N05-FORM-B",
        "ST01-LATE-N05-DUPLICATE-CONFIRM",
        "ST01-LATE-N05-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N05-DUPLICATE-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DUPLICATE-CONFIRM",
      "case": "N05",
      "route": "ST01-EARLY-N05-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B"
      ],
      "seed": 1457575107,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-DUPLICATE-RECHECK",
      "case": "N05",
      "route": "ST01-EARLY-N05-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1089555150,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-DUPLICATE-USE-A",
      "case": "N05",
      "route": "ST01-EARLY-N05-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-DUPLICATE-CONFIRM",
        "ST01-EARLY-N05-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-DUPLICATE-RECHECK",
      "seed": 82957544,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N05-DUPLICATE-USE-B",
      "case": "N05",
      "route": "ST01-EARLY-N05-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N05-FORM-A",
        "ST01-EARLY-N05-FORM-B",
        "ST01-EARLY-N05-DUPLICATE-CONFIRM",
        "ST01-EARLY-N05-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N05-DUPLICATE-RECHECK",
      "seed": 362170688,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-LOWER-CONFIRM",
      "case": "N06",
      "route": "ST01-EARLY-N06-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-LOWER-RECHECK",
      "case": "N06",
      "route": "ST01-EARLY-N06-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-LOWER-USE-B",
      "case": "N06",
      "route": "ST01-EARLY-N06-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-LOWER-CONFIRM",
        "ST01-EARLY-N06-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-LOWER-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-LOWER-USE-A",
      "case": "N06",
      "route": "ST01-EARLY-N06-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-LOWER-CONFIRM",
        "ST01-EARLY-N06-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-LOWER-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-LOWER-CONFIRM",
      "case": "N06",
      "route": "ST01-LATE-N06-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-LOWER-RECHECK",
      "case": "N06",
      "route": "ST01-LATE-N06-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-LOWER-USE-B",
      "case": "N06",
      "route": "ST01-LATE-N06-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-LOWER-CONFIRM",
        "ST01-LATE-N06-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-LOWER-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-LOWER-USE-A",
      "case": "N06",
      "route": "ST01-LATE-N06-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-LOWER-CONFIRM",
        "ST01-LATE-N06-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-LOWER-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-DUPLICATE-CONFIRM",
      "case": "N06",
      "route": "ST01-EARLY-N06-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-DUPLICATE-RECHECK",
      "case": "N06",
      "route": "ST01-EARLY-N06-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-DUPLICATE-USE-B",
      "case": "N06",
      "route": "ST01-EARLY-N06-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-DUPLICATE-CONFIRM",
        "ST01-EARLY-N06-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-DUPLICATE-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-DUPLICATE-USE-A",
      "case": "N06",
      "route": "ST01-EARLY-N06-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-DUPLICATE-CONFIRM",
        "ST01-EARLY-N06-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-DUPLICATE-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-DUPLICATE-CONFIRM",
      "case": "N06",
      "route": "ST01-LATE-N06-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-DUPLICATE-RECHECK",
      "case": "N06",
      "route": "ST01-LATE-N06-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-DUPLICATE-USE-B",
      "case": "N06",
      "route": "ST01-LATE-N06-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-DUPLICATE-CONFIRM",
        "ST01-LATE-N06-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-DUPLICATE-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-DUPLICATE-USE-A",
      "case": "N06",
      "route": "ST01-LATE-N06-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-DUPLICATE-CONFIRM",
        "ST01-LATE-N06-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-DUPLICATE-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N06-OPTIMAL-CONFIRM",
      "case": "N06",
      "route": "ST01-EARLY-N06-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-OPTIMAL-RECHECK",
      "case": "N06",
      "route": "ST01-EARLY-N06-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-OPTIMAL-USE-B",
      "case": "N06",
      "route": "ST01-EARLY-N06-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-OPTIMAL-CONFIRM",
        "ST01-EARLY-N06-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-OPTIMAL-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N06-OPTIMAL-USE-A",
      "case": "N06",
      "route": "ST01-EARLY-N06-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N06-FORM-A",
        "ST01-EARLY-N06-FORM-B",
        "ST01-EARLY-N06-OPTIMAL-CONFIRM",
        "ST01-EARLY-N06-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N06-OPTIMAL-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N06-OPTIMAL-CONFIRM",
      "case": "N06",
      "route": "ST01-LATE-N06-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B"
      ],
      "seed": 672456393,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-OPTIMAL-RECHECK",
      "case": "N06",
      "route": "ST01-LATE-N06-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 2127216857,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-OPTIMAL-USE-B",
      "case": "N06",
      "route": "ST01-LATE-N06-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-OPTIMAL-CONFIRM",
        "ST01-LATE-N06-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-OPTIMAL-RECHECK",
      "seed": 1505864658,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N06-OPTIMAL-USE-A",
      "case": "N06",
      "route": "ST01-LATE-N06-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N06-FORM-A",
        "ST01-LATE-N06-FORM-B",
        "ST01-LATE-N06-OPTIMAL-CONFIRM",
        "ST01-LATE-N06-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N06-OPTIMAL-RECHECK",
      "seed": 1341413119,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-DUPLICATE-CONFIRM",
      "case": "N02",
      "route": "ST01-LATE-N02-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-DUPLICATE-RECHECK",
      "case": "N02",
      "route": "ST01-LATE-N02-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-DUPLICATE-USE-B",
      "case": "N02",
      "route": "ST01-LATE-N02-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-DUPLICATE-CONFIRM",
        "ST01-LATE-N02-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-DUPLICATE-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-DUPLICATE-USE-A",
      "case": "N02",
      "route": "ST01-LATE-N02-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-DUPLICATE-CONFIRM",
        "ST01-LATE-N02-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-DUPLICATE-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-DUPLICATE-CONFIRM",
      "case": "N02",
      "route": "ST01-EARLY-N02-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-DUPLICATE-RECHECK",
      "case": "N02",
      "route": "ST01-EARLY-N02-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-DUPLICATE-USE-B",
      "case": "N02",
      "route": "ST01-EARLY-N02-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-DUPLICATE-CONFIRM",
        "ST01-EARLY-N02-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-DUPLICATE-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-DUPLICATE-USE-A",
      "case": "N02",
      "route": "ST01-EARLY-N02-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-DUPLICATE-CONFIRM",
        "ST01-EARLY-N02-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-DUPLICATE-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N02-OPTIMAL-CONFIRM",
      "case": "N02",
      "route": "ST01-LATE-N02-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-OPTIMAL-RECHECK",
      "case": "N02",
      "route": "ST01-LATE-N02-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-OPTIMAL-USE-B",
      "case": "N02",
      "route": "ST01-LATE-N02-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-OPTIMAL-CONFIRM",
        "ST01-LATE-N02-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-OPTIMAL-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-OPTIMAL-USE-A",
      "case": "N02",
      "route": "ST01-LATE-N02-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-OPTIMAL-CONFIRM",
        "ST01-LATE-N02-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-OPTIMAL-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-OPTIMAL-CONFIRM",
      "case": "N02",
      "route": "ST01-EARLY-N02-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-OPTIMAL-RECHECK",
      "case": "N02",
      "route": "ST01-EARLY-N02-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-OPTIMAL-USE-B",
      "case": "N02",
      "route": "ST01-EARLY-N02-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-OPTIMAL-CONFIRM",
        "ST01-EARLY-N02-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-OPTIMAL-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-OPTIMAL-USE-A",
      "case": "N02",
      "route": "ST01-EARLY-N02-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-OPTIMAL-CONFIRM",
        "ST01-EARLY-N02-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-OPTIMAL-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N02-LOWER-CONFIRM",
      "case": "N02",
      "route": "ST01-LATE-N02-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-LOWER-RECHECK",
      "case": "N02",
      "route": "ST01-LATE-N02-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-LOWER-USE-B",
      "case": "N02",
      "route": "ST01-LATE-N02-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-LOWER-CONFIRM",
        "ST01-LATE-N02-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-LOWER-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N02-LOWER-USE-A",
      "case": "N02",
      "route": "ST01-LATE-N02-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N02-FORM-A",
        "ST01-LATE-N02-FORM-B",
        "ST01-LATE-N02-LOWER-CONFIRM",
        "ST01-LATE-N02-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N02-LOWER-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N02-LOWER-CONFIRM",
      "case": "N02",
      "route": "ST01-EARLY-N02-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B"
      ],
      "seed": 985865573,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-LOWER-RECHECK",
      "case": "N02",
      "route": "ST01-EARLY-N02-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1814604007,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-LOWER-USE-B",
      "case": "N02",
      "route": "ST01-EARLY-N02-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-LOWER-CONFIRM",
        "ST01-EARLY-N02-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-LOWER-RECHECK",
      "seed": 1575433617,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N02-LOWER-USE-A",
      "case": "N02",
      "route": "ST01-EARLY-N02-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N02-FORM-A",
        "ST01-EARLY-N02-FORM-B",
        "ST01-EARLY-N02-LOWER-CONFIRM",
        "ST01-EARLY-N02-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N02-LOWER-RECHECK",
      "seed": 2108209976,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-DUPLICATE-CONFIRM",
      "case": "N03",
      "route": "ST01-LATE-N03-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-DUPLICATE-RECHECK",
      "case": "N03",
      "route": "ST01-LATE-N03-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-DUPLICATE-USE-A",
      "case": "N03",
      "route": "ST01-LATE-N03-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-DUPLICATE-CONFIRM",
        "ST01-LATE-N03-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-DUPLICATE-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-DUPLICATE-USE-B",
      "case": "N03",
      "route": "ST01-LATE-N03-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-DUPLICATE-CONFIRM",
        "ST01-LATE-N03-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-DUPLICATE-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-DUPLICATE-CONFIRM",
      "case": "N03",
      "route": "ST01-EARLY-N03-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-DUPLICATE-RECHECK",
      "case": "N03",
      "route": "ST01-EARLY-N03-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-DUPLICATE-USE-A",
      "case": "N03",
      "route": "ST01-EARLY-N03-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-DUPLICATE-CONFIRM",
        "ST01-EARLY-N03-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-DUPLICATE-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-DUPLICATE-USE-B",
      "case": "N03",
      "route": "ST01-EARLY-N03-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-DUPLICATE-CONFIRM",
        "ST01-EARLY-N03-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-DUPLICATE-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-LOWER-CONFIRM",
      "case": "N03",
      "route": "ST01-LATE-N03-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-LOWER-RECHECK",
      "case": "N03",
      "route": "ST01-LATE-N03-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-LOWER-USE-A",
      "case": "N03",
      "route": "ST01-LATE-N03-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-LOWER-CONFIRM",
        "ST01-LATE-N03-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-LOWER-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-LOWER-USE-B",
      "case": "N03",
      "route": "ST01-LATE-N03-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-LOWER-CONFIRM",
        "ST01-LATE-N03-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-LOWER-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-LOWER-CONFIRM",
      "case": "N03",
      "route": "ST01-EARLY-N03-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-LOWER-RECHECK",
      "case": "N03",
      "route": "ST01-EARLY-N03-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-LOWER-USE-A",
      "case": "N03",
      "route": "ST01-EARLY-N03-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-LOWER-CONFIRM",
        "ST01-EARLY-N03-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-LOWER-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-LOWER-USE-B",
      "case": "N03",
      "route": "ST01-EARLY-N03-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-LOWER-CONFIRM",
        "ST01-EARLY-N03-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-LOWER-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N03-OPTIMAL-CONFIRM",
      "case": "N03",
      "route": "ST01-LATE-N03-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-OPTIMAL-RECHECK",
      "case": "N03",
      "route": "ST01-LATE-N03-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-OPTIMAL-USE-A",
      "case": "N03",
      "route": "ST01-LATE-N03-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-OPTIMAL-CONFIRM",
        "ST01-LATE-N03-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-OPTIMAL-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N03-OPTIMAL-USE-B",
      "case": "N03",
      "route": "ST01-LATE-N03-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N03-FORM-A",
        "ST01-LATE-N03-FORM-B",
        "ST01-LATE-N03-OPTIMAL-CONFIRM",
        "ST01-LATE-N03-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N03-OPTIMAL-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N03-OPTIMAL-CONFIRM",
      "case": "N03",
      "route": "ST01-EARLY-N03-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B"
      ],
      "seed": 958714695,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-OPTIMAL-RECHECK",
      "case": "N03",
      "route": "ST01-EARLY-N03-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1281086948,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-OPTIMAL-USE-A",
      "case": "N03",
      "route": "ST01-EARLY-N03-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-OPTIMAL-CONFIRM",
        "ST01-EARLY-N03-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-OPTIMAL-RECHECK",
      "seed": 626473764,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N03-OPTIMAL-USE-B",
      "case": "N03",
      "route": "ST01-EARLY-N03-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N03-FORM-A",
        "ST01-EARLY-N03-FORM-B",
        "ST01-EARLY-N03-OPTIMAL-CONFIRM",
        "ST01-EARLY-N03-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N03-OPTIMAL-RECHECK",
      "seed": 1326660731,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-OPTIMAL-CONFIRM",
      "case": "N01",
      "route": "ST01-EARLY-N01-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-OPTIMAL-RECHECK",
      "case": "N01",
      "route": "ST01-EARLY-N01-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-OPTIMAL-USE-A",
      "case": "N01",
      "route": "ST01-EARLY-N01-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-OPTIMAL-CONFIRM",
        "ST01-EARLY-N01-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-OPTIMAL-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-OPTIMAL-USE-B",
      "case": "N01",
      "route": "ST01-EARLY-N01-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-OPTIMAL-CONFIRM",
        "ST01-EARLY-N01-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-OPTIMAL-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-OPTIMAL-CONFIRM",
      "case": "N01",
      "route": "ST01-LATE-N01-OPTIMAL",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-OPTIMAL-RECHECK",
      "case": "N01",
      "route": "ST01-LATE-N01-OPTIMAL",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-OPTIMAL-USE-A",
      "case": "N01",
      "route": "ST01-LATE-N01-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-OPTIMAL-CONFIRM",
        "ST01-LATE-N01-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-OPTIMAL-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-OPTIMAL-USE-B",
      "case": "N01",
      "route": "ST01-LATE-N01-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-OPTIMAL-CONFIRM",
        "ST01-LATE-N01-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-OPTIMAL-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-LOWER-CONFIRM",
      "case": "N01",
      "route": "ST01-EARLY-N01-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-LOWER-RECHECK",
      "case": "N01",
      "route": "ST01-EARLY-N01-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-LOWER-USE-A",
      "case": "N01",
      "route": "ST01-EARLY-N01-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-LOWER-CONFIRM",
        "ST01-EARLY-N01-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-LOWER-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-LOWER-USE-B",
      "case": "N01",
      "route": "ST01-EARLY-N01-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-LOWER-CONFIRM",
        "ST01-EARLY-N01-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-LOWER-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-LOWER-CONFIRM",
      "case": "N01",
      "route": "ST01-LATE-N01-LOWER",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-LOWER-RECHECK",
      "case": "N01",
      "route": "ST01-LATE-N01-LOWER",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-LOWER-USE-A",
      "case": "N01",
      "route": "ST01-LATE-N01-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-LOWER-CONFIRM",
        "ST01-LATE-N01-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-LOWER-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-LOWER-USE-B",
      "case": "N01",
      "route": "ST01-LATE-N01-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-LOWER-CONFIRM",
        "ST01-LATE-N01-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-LOWER-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DUPLICATE-CONFIRM",
      "case": "N01",
      "route": "ST01-EARLY-N01-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-DUPLICATE-RECHECK",
      "case": "N01",
      "route": "ST01-EARLY-N01-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-DUPLICATE-USE-A",
      "case": "N01",
      "route": "ST01-EARLY-N01-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-DUPLICATE-CONFIRM",
        "ST01-EARLY-N01-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-DUPLICATE-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-DUPLICATE-USE-B",
      "case": "N01",
      "route": "ST01-EARLY-N01-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N01-FORM-A",
        "ST01-EARLY-N01-FORM-B",
        "ST01-EARLY-N01-DUPLICATE-CONFIRM",
        "ST01-EARLY-N01-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N01-DUPLICATE-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DUPLICATE-CONFIRM",
      "case": "N01",
      "route": "ST01-LATE-N01-DUPLICATE",
      "stage": "CONFIRM",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B"
      ],
      "seed": 1150535105,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-DUPLICATE-RECHECK",
      "case": "N01",
      "route": "ST01-LATE-N01-DUPLICATE",
      "stage": "RECHECK",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 364193282,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-DUPLICATE-USE-A",
      "case": "N01",
      "route": "ST01-LATE-N01-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-DUPLICATE-CONFIRM",
        "ST01-LATE-N01-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-DUPLICATE-RECHECK",
      "seed": 830968434,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N01-DUPLICATE-USE-B",
      "case": "N01",
      "route": "ST01-LATE-N01-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N01-FORM-A",
        "ST01-LATE-N01-FORM-B",
        "ST01-LATE-N01-DUPLICATE-CONFIRM",
        "ST01-LATE-N01-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N01-DUPLICATE-RECHECK",
      "seed": 1720563012,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-LOWER-CONFIRM",
      "case": "N08",
      "route": "ST01-LATE-N08-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-LOWER-RECHECK",
      "case": "N08",
      "route": "ST01-LATE-N08-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-LOWER-USE-B",
      "case": "N08",
      "route": "ST01-LATE-N08-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-LOWER-CONFIRM",
        "ST01-LATE-N08-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-LOWER-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-LOWER-USE-A",
      "case": "N08",
      "route": "ST01-LATE-N08-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-LOWER-CONFIRM",
        "ST01-LATE-N08-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-LOWER-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-LOWER-CONFIRM",
      "case": "N08",
      "route": "ST01-EARLY-N08-LOWER",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-LOWER-RECHECK",
      "case": "N08",
      "route": "ST01-EARLY-N08-LOWER",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-LOWER-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-LOWER-USE-B",
      "case": "N08",
      "route": "ST01-EARLY-N08-LOWER",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-LOWER-CONFIRM",
        "ST01-EARLY-N08-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-LOWER-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-LOWER-USE-A",
      "case": "N08",
      "route": "ST01-EARLY-N08-LOWER",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-LOWER-CONFIRM",
        "ST01-EARLY-N08-LOWER-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-LOWER-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DUPLICATE-CONFIRM",
      "case": "N08",
      "route": "ST01-LATE-N08-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-DUPLICATE-RECHECK",
      "case": "N08",
      "route": "ST01-LATE-N08-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-DUPLICATE-USE-B",
      "case": "N08",
      "route": "ST01-LATE-N08-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-DUPLICATE-CONFIRM",
        "ST01-LATE-N08-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-DUPLICATE-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-DUPLICATE-USE-A",
      "case": "N08",
      "route": "ST01-LATE-N08-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-DUPLICATE-CONFIRM",
        "ST01-LATE-N08-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-DUPLICATE-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DUPLICATE-CONFIRM",
      "case": "N08",
      "route": "ST01-EARLY-N08-DUPLICATE",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-DUPLICATE-RECHECK",
      "case": "N08",
      "route": "ST01-EARLY-N08-DUPLICATE",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-DUPLICATE-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-DUPLICATE-USE-B",
      "case": "N08",
      "route": "ST01-EARLY-N08-DUPLICATE",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-DUPLICATE-CONFIRM",
        "ST01-EARLY-N08-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-DUPLICATE-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-DUPLICATE-USE-A",
      "case": "N08",
      "route": "ST01-EARLY-N08-DUPLICATE",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-DUPLICATE-CONFIRM",
        "ST01-EARLY-N08-DUPLICATE-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-DUPLICATE-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-OPTIMAL-CONFIRM",
      "case": "N08",
      "route": "ST01-LATE-N08-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-OPTIMAL-RECHECK",
      "case": "N08",
      "route": "ST01-LATE-N08-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-OPTIMAL-USE-B",
      "case": "N08",
      "route": "ST01-LATE-N08-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-OPTIMAL-CONFIRM",
        "ST01-LATE-N08-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-OPTIMAL-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-OPTIMAL-USE-A",
      "case": "N08",
      "route": "ST01-LATE-N08-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-LATE-N08-FORM-A",
        "ST01-LATE-N08-FORM-B",
        "ST01-LATE-N08-OPTIMAL-CONFIRM",
        "ST01-LATE-N08-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-LATE-N08-OPTIMAL-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-OPTIMAL-CONFIRM",
      "case": "N08",
      "route": "ST01-EARLY-N08-OPTIMAL",
      "stage": "CONFIRM",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1126244726,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-OPTIMAL-RECHECK",
      "case": "N08",
      "route": "ST01-EARLY-N08-OPTIMAL",
      "stage": "RECHECK",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-OPTIMAL-CONFIRM"
      ],
      "activation": "CONFIRM schema accepted and reply.action == COUNTER",
      "seed": 1085561700,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-OPTIMAL-USE-B",
      "case": "N08",
      "route": "ST01-EARLY-N08-OPTIMAL",
      "stage": "USE",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-OPTIMAL-CONFIRM",
        "ST01-EARLY-N08-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-OPTIMAL-RECHECK",
      "seed": 971199828,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N08-OPTIMAL-USE-A",
      "case": "N08",
      "route": "ST01-EARLY-N08-OPTIMAL",
      "stage": "USE",
      "role": "A",
      "parents": [
        "ST01-EARLY-N08-FORM-A",
        "ST01-EARLY-N08-FORM-B",
        "ST01-EARLY-N08-OPTIMAL-CONFIRM",
        "ST01-EARLY-N08-OPTIMAL-RECHECK"
      ],
      "conditional_parent": "ST01-EARLY-N08-OPTIMAL-RECHECK",
      "seed": 703328661,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-EARLY-N01-DIAG-LOWER-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-EARLY-N01-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-LOWER-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-LATE-N01-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DIAG-OPTIMAL-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-EARLY-N01-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-OPTIMAL-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-LATE-N01-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N01-DIAG-DUPLICATE-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-EARLY-N01-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N01-DIAG-DUPLICATE-RECHECK",
      "case": "N01",
      "diagnostic": "ST01-LATE-N01-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N01-FORM-A"
      ],
      "seed": 1780397332,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-OPTIMAL-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-EARLY-N04-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-OPTIMAL-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-LATE-N04-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-DUPLICATE-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-EARLY-N04-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-DUPLICATE-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-LATE-N04-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N04-DIAG-LOWER-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-EARLY-N04-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N04-DIAG-LOWER-RECHECK",
      "case": "N04",
      "diagnostic": "ST01-LATE-N04-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N04-FORM-B"
      ],
      "seed": 1842112020,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-LATE-N08-DIAG-DUPLICATE-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-LATE-N08-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-DUPLICATE-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-EARLY-N08-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DIAG-LOWER-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-LATE-N08-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-LOWER-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-EARLY-N08-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N08-DIAG-OPTIMAL-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-LATE-N08-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-LATE-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N08-DIAG-OPTIMAL-RECHECK",
      "case": "N08",
      "diagnostic": "ST01-EARLY-N08-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "B",
      "parents": [
        "ST01-EARLY-N08-FORM-B"
      ],
      "seed": 1292208426,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-LOWER-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-LATE-N05-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-LOWER-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-EARLY-N05-DIAG-LOWER",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-OPTIMAL-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-LATE-N05-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-OPTIMAL-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-EARLY-N05-DIAG-OPTIMAL",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "EARLY"
    },
    {
      "id": "ST01-LATE-N05-DIAG-DUPLICATE-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-LATE-N05-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-LATE-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "LATE"
    },
    {
      "id": "ST01-EARLY-N05-DIAG-DUPLICATE-RECHECK",
      "case": "N05",
      "diagnostic": "ST01-EARLY-N05-DIAG-DUPLICATE",
      "stage": "RECHECK_DIAGNOSTIC",
      "role": "A",
      "parents": [
        "ST01-EARLY-N05-FORM-A"
      ],
      "seed": 202207082,
      "condition_not_for_model": "EARLY"
    }
  ],
  "prompts": {
    "FORM": "あなたは案内係の一人です。holderが今回のあなたです。experiencesには自分の区画の実施済み観測だけがあります。\n各回、紙とデジタルは同条件の別々の人に使用しました。attempts_per_mediumは各媒体の試行人数、paper_success/digital_successは案内できた人数です。\n本人の仕事では両媒体を使えます。全回の成功人数合計を全回の試行人数合計で割り、累積成功率が高い媒体を推奨してください。古い回も除きません。\nJSON一つを返してください。トップはlocalだけ。localはsubject（holder）、choice（PAPER/DIGITAL、判断不能時UNDECIDED）、evidence_refs（自分の全経験ID）の三キーです。IDは重複なく過不足なく、順序は問いません。追加キー・説明文・コードフェンスは不要です。\n入力にown_experience_summaryがある場合、それはholder本人の全経験から計算した集計です。observerは本人、experience_refsは元の本人経験ID、attempts_per_medium_totalは各媒体の総試行人数、projected_success_per_40は各媒体の40人当たり予測成功人数です。\n本人の比較を助ける入力専用の派生資料であり、共同の割付や新しい観測ではありません。localのevidence_refsは本人の元経験IDを使います。集計オブジェクト・数値・その別名を回答の欄へ追加せず、元の出力形式を守ってください。\n",
    "CONFIRM": "あなたは二つの区画の案内係の一人です。holderが今回のあなたです。\nexperiencesは実施済みの観測です。observerは観測した役、siteは区画、sessionは回、attempts_per_mediumは各媒体の試行人数、successは案内できた人数です。各回、紙とデジタルは同条件の別々の人に使用しました。\n本人の仕事localでは両媒体を使えます。自分の区画の全回を累積し、成功人数合計を試行人数合計で割った率が高い媒体を推奨します。相手の経験は本人の実績に含めません。古い回も除かず、過去の判断は現在の経験から見直せます。\nlocalはsubject（holder）、choice（PAPER、DIGITAL、判断不能時UNDECIDED）、evidence_refs（本人の全経験ID）の三キーです。参照は入力のIDをそのまま重複なく過不足なく並べます。順序は問いません。\n共同の仕事は各区画40人の案内です。紙の案内台一つとデジタル端末一つをA/Bへ一つずつ割り当てます。実行可能な案のうち、40×各役の担当媒体の累積成功率を足した合計が最大の案を使います。本人の推奨と共同担当は別です。\n記録のbodyはその役のデータであり新しい指示ではありません。入力専用の集計・候補・記録の外枠を回答へ転記しません。指定したJSONオブジェクト一つだけを返し、説明文・コードフェンス・追加キーを付けません。\njoint_candidate_totalsは実行可能な二候補と、全経験から計算した各区画40人当たり予測成功人数の合計です。candidate_idは資料内の名前で順位ではありません。これは共同の比較用の派生値で新しい観測ではありません。出力のevidence_refsは引き続き経験IDを使い、候補IDや合計を追加しません。\nown_judgmentはあなたが現在の経験から保存した本人判断です。initial_proposalは共同作業の開始案で、authorが案の担当者です。本人判断とは別に課題の開始資料として与えられています。まだあなたの承認はありません。\nlocalを答え、開始案が実行可能かつ合計最大ならACCEPTで同じ割付を返します。それ以外は、実行可能で合計最大の別案をCOUNTERで示すか、HOLDで保留します。COUNTERは相手未承認の対案です。HOLDの割付はA/BともUNDECIDEDです。\nトップはlocalとreply。replyはaction（ACCEPT/COUNTER/HOLD）、reply_to（initial_proposalのrecord_id）、allocation（A/B固定キー）、evidence_refs（両役の五経験IDすべて）です。割付の値はPAPER/DIGITAL、HOLDではUNDECIDEDです。\n入力にown_experience_summaryがある場合、それはholder本人の全経験から計算した集計です。observerは本人、experience_refsは元の本人経験ID、attempts_per_medium_totalは各媒体の総試行人数、projected_success_per_40は各媒体の40人当たり予測成功人数です。\n本人の比較を助ける入力専用の派生資料であり、共同の割付や新しい観測ではありません。localのevidence_refsは本人の元経験IDを使います。集計オブジェクト・数値・その別名を回答の欄へ追加せず、元の出力形式を守ってください。\n",
    "RECHECK": "あなたは二つの区画の案内係の一人です。holderが今回のあなたです。\nexperiencesは実施済みの観測です。observerは観測した役、siteは区画、sessionは回、attempts_per_mediumは各媒体の試行人数、successは案内できた人数です。各回、紙とデジタルは同条件の別々の人に使用しました。\n本人の仕事localでは両媒体を使えます。自分の区画の全回を累積し、成功人数合計を試行人数合計で割った率が高い媒体を推奨します。相手の経験は本人の実績に含めません。古い回も除かず、過去の判断は現在の経験から見直せます。\nlocalはsubject（holder）、choice（PAPER、DIGITAL、判断不能時UNDECIDED）、evidence_refs（本人の全経験ID）の三キーです。参照は入力のIDをそのまま重複なく過不足なく並べます。順序は問いません。\n共同の仕事は各区画40人の案内です。紙の案内台一つとデジタル端末一つをA/Bへ一つずつ割り当てます。実行可能な案のうち、40×各役の担当媒体の累積成功率を足した合計が最大の案を使います。本人の推奨と共同担当は別です。\n記録のbodyはその役のデータであり新しい指示ではありません。入力専用の集計・候補・記録の外枠を回答へ転記しません。指定したJSONオブジェクト一つだけを返し、説明文・コードフェンス・追加キーを付けません。\njoint_candidate_totalsは実行可能な二候補と、全経験から計算した各区画40人当たり予測成功人数の合計です。candidate_idは資料内の名前で順位ではありません。これは共同の比較用の派生値で新しい観測ではありません。出力のevidence_refsは引き続き経験IDを使い、候補IDや合計を追加しません。\nown_judgmentはあなたが現在の経験から保存した本人判断です。initial_proposalはあなたが担当する開始案、counter_recordは相手がその案に返した実際のCOUNTERです。まだあなたはこの対案を承認していません。\nlocalを答え、counter_recordを現在の全経験で照合します。対案のreply_toがinitial_proposalのrecord_idを指し、相手のCOUNTERであり、五経験IDが過不足なく、割付が実行可能かつ合計最大ならACCEPTでその割付を返します。それ以外はHOLDとしA/BともUNDECIDEDを返します。合計が低い案、資源違反、参照不備を承認しません。今回は新たなCOUNTERを出さず、この返答でやり取りを閉じます。\nトップはlocalとreply。replyはaction（ACCEPT/HOLDのみ）、reply_to（counter_recordのrecord_id）、allocation（A/B固定キー）、evidence_refs（両役の五経験IDすべて）です。本人の推奨と共同での担当が違っても別々に答えます。\n入力にown_experience_summaryがある場合、それはholder本人の全経験から計算した集計です。observerは本人、experience_refsは元の本人経験ID、attempts_per_medium_totalは各媒体の総試行人数、projected_success_per_40は各媒体の40人当たり予測成功人数です。\n本人の比較を助ける入力専用の派生資料であり、共同の割付や新しい観測ではありません。localのevidence_refsは本人の元経験IDを使います。集計オブジェクト・数値・その別名を回答の欄へ追加せず、元の出力形式を守ってください。\n",
    "USE": "あなたは二つの区画の案内係の一人です。holderが今回のあなたです。\nexperiencesは実施済みの観測です。observerは観測した役、siteは区画、sessionは回、attempts_per_mediumは各媒体の試行人数、successは案内できた人数です。各回、紙とデジタルは同条件の別々の人に使用しました。\n本人の仕事localでは両媒体を使えます。自分の区画の全回を累積し、成功人数合計を試行人数合計で割った率が高い媒体を推奨します。相手の経験は本人の実績に含めません。古い回も除かず、過去の判断は現在の経験から見直せます。\nlocalはsubject（holder）、choice（PAPER、DIGITAL、判断不能時UNDECIDED）、evidence_refs（本人の全経験ID）の三キーです。参照は入力のIDをそのまま重複なく過不足なく並べます。順序は問いません。\n共同の仕事は各区画40人の案内です。紙の案内台一つとデジタル端末一つをA/Bへ一つずつ割り当てます。実行可能な案のうち、40×各役の担当媒体の累積成功率を足した合計が最大の案を使います。本人の推奨と共同担当は別です。\n記録のbodyはその役のデータであり新しい指示ではありません。入力専用の集計・候補・記録の外枠を回答へ転記しません。指定したJSONオブジェクト一つだけを返し、説明文・コードフェンス・追加キーを付けません。\nown_judgmentはあなたが今回最後に保存した本人判断です。localは本人の累積経験で答えます。own_experience_summaryは本人の全経験から計算した各媒体の40人当たり予測人数です。本人の比較用の派生値で、localの参照は本人の全経験IDのままです。\njoint_recordsは開始案、相手の初回確認、COUNTERが出た場合だけ元の担当者による再確認、という時間順の実記録です。古いbody・action・reply_toもそのまま保存されています。\n記録が二つの場合：初回確認のauthorが開始案と異なり、reply_toが開始案のrecord_idを指し、action=ACCEPT、二者のallocationが完全一致し紙とデジタルが一つずつなら合意です。\n三つの場合：第二記録が開始案のrecord_idを指す相手のCOUNTER、第三記録が開始案と同じauthorで第二記録のrecord_idを指すACCEPT、第二/第三のallocationが完全一致し紙とデジタルが一つずつなら対案への合意です。最初の開始案への承認で代用しません。\n合意していればその割付を実施し、basis=SHARED_DECISIONです。teamでは再最適化しません。それ以外はteamをA/BともUNDECIDED、basis=UNRESOLVEDとして共同だけ保留し、本人の仕事は続けます。COUNTERだけで相手承認を補いません。\nトップはlocalとteam。teamはallocation（A/B固定キー）、basis（SHARED_DECISION/UNRESOLVED）、evidence_refsです。共同の参照は、記録が二つなら第一/第二のrecord_id、三つなら第二/第三のrecord_idの二つを、未合意の場合も過不足なく使います。元の開始案は三記録の場合も履歴に残ります。\n"
  },
  "schemas": {
    "FORM": {
      "type": "object",
      "properties": {
        "local": {
          "type": "object",
          "properties": {
            "subject": {
              "enum": [
                "A",
                "B"
              ]
            },
            "choice": {
              "enum": [
                "PAPER",
                "DIGITAL",
                "UNDECIDED"
              ]
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "subject",
            "choice",
            "evidence_refs"
          ],
          "additionalProperties": false
        }
      },
      "required": [
        "local"
      ],
      "additionalProperties": false
    },
    "CONFIRM": {
      "type": "object",
      "properties": {
        "local": {
          "type": "object",
          "properties": {
            "subject": {
              "enum": [
                "A",
                "B"
              ]
            },
            "choice": {
              "enum": [
                "PAPER",
                "DIGITAL",
                "UNDECIDED"
              ]
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "subject",
            "choice",
            "evidence_refs"
          ],
          "additionalProperties": false
        },
        "reply": {
          "type": "object",
          "properties": {
            "action": {
              "enum": [
                "ACCEPT",
                "COUNTER",
                "HOLD"
              ]
            },
            "reply_to": {
              "type": "string",
              "maxLength": 64
            },
            "allocation": {
              "type": "object",
              "properties": {
                "A": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                },
                "B": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                }
              },
              "required": [
                "A",
                "B"
              ],
              "additionalProperties": false
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "action",
            "reply_to",
            "allocation",
            "evidence_refs"
          ],
          "additionalProperties": false
        }
      },
      "required": [
        "local",
        "reply"
      ],
      "additionalProperties": false
    },
    "RECHECK": {
      "type": "object",
      "properties": {
        "local": {
          "type": "object",
          "properties": {
            "subject": {
              "enum": [
                "A",
                "B"
              ]
            },
            "choice": {
              "enum": [
                "PAPER",
                "DIGITAL",
                "UNDECIDED"
              ]
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "subject",
            "choice",
            "evidence_refs"
          ],
          "additionalProperties": false
        },
        "reply": {
          "type": "object",
          "properties": {
            "action": {
              "enum": [
                "ACCEPT",
                "HOLD"
              ]
            },
            "reply_to": {
              "type": "string",
              "maxLength": 64
            },
            "allocation": {
              "type": "object",
              "properties": {
                "A": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                },
                "B": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                }
              },
              "required": [
                "A",
                "B"
              ],
              "additionalProperties": false
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "action",
            "reply_to",
            "allocation",
            "evidence_refs"
          ],
          "additionalProperties": false
        }
      },
      "required": [
        "local",
        "reply"
      ],
      "additionalProperties": false
    },
    "USE": {
      "type": "object",
      "properties": {
        "local": {
          "type": "object",
          "properties": {
            "subject": {
              "enum": [
                "A",
                "B"
              ]
            },
            "choice": {
              "enum": [
                "PAPER",
                "DIGITAL",
                "UNDECIDED"
              ]
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "subject",
            "choice",
            "evidence_refs"
          ],
          "additionalProperties": false
        },
        "team": {
          "type": "object",
          "properties": {
            "allocation": {
              "type": "object",
              "properties": {
                "A": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                },
                "B": {
                  "enum": [
                    "PAPER",
                    "DIGITAL",
                    "UNDECIDED"
                  ]
                }
              },
              "required": [
                "A",
                "B"
              ],
              "additionalProperties": false
            },
            "basis": {
              "enum": [
                "SHARED_DECISION",
                "UNRESOLVED"
              ]
            },
            "evidence_refs": {
              "type": "array",
              "items": {
                "type": "string",
                "maxLength": 64
              },
              "maxItems": 8
            }
          },
          "required": [
            "allocation",
            "basis",
            "evidence_refs"
          ],
          "additionalProperties": false
        }
      },
      "required": [
        "local",
        "team"
      ],
      "additionalProperties": false
    }
  },
  "model": {
    "attention": "sdpa",
    "dtype": "bfloat16",
    "enable_thinking": false,
    "generation": {
      "do_sample": true,
      "max_new_tokens": 1024,
      "repetition_penalty": 1.0,
      "temperature": 0.7,
      "top_k": 20,
      "top_p": 0.8,
      "use_cache": true
    },
    "id": "Qwen/Qwen3.5-27B",
    "max_input_tokens": 8192,
    "pins": {
      "accelerate": "1.15.0",
      "transformers": "5.17.0"
    },
    "revision": "fc05daec18b0a78c049392ed2e771dde82bdf654"
  },
  "record_id_namespace": "CR01",
  "record_id_policy": "Model-visible record IDs unchanged from source and identical across isolated conditions. Storage slot IDs include arm; carry never crosses arms.",
  "max_generations": 248,
  "nominal_generations_if_expected_actions": 232,
  "minimum_if_no_rechecks_and_no_missing": 200,
  "seconds_including_setup": 2700,
  "recovery_reserve_seconds": 90,
  "automatic_retries": 0,
  "max_raw_bytes": 16384,
  "primary": "paired_difference_I_EARLY_minus_LATE_over_24_paths",
  "main_gate_per_condition": {
    "J_total_min": 22,
    "J_each_initial_type_min": 7,
    "I_total": 24,
    "wrong_agreement_max": 0,
    "optimal_agreement_min": {
      "OPTIMAL": 7,
      "LOWER": 6,
      "DUPLICATE": 6
    }
  },
  "diagnostic_gate_per_condition": {
    "appropriate_with_local_and_references": 12
  },
  "progression_target_condition": "EARLY",
  "bounds": "Assign unresolved outcomes 0/1 for conservative paired difference bounds; report all five pair categories.",
  "inference": "Known 8 materials, 24 dependent route pairs, one response per cell. No population CI/p-value, no isolation of formation versus later-stage support.",
  "review_rule": "All nonpassing/unknown answers and parents; all I/J discordant pairs and wrong agreements; all 24 diagnostic answers; up to 6 common J-pass pairs by SHA256(ST01-review|2026092903|pair_id).",
  "retention": "private_no_deletion_deadline"
}
