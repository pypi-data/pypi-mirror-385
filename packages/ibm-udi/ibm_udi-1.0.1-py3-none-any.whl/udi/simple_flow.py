simple_flow_payload = {
    "container_kind": "project",
    "container_id": "caa9a282-579b-41c0-ab83-d611e4083154",
    "name": "udp_lf_py_all_10dec743pm",
    "description": "",
    "definition": {
        "doc_type": "pipeline",
        "version": "3.0",
        "json_schema": "https://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json",
        "id": "55578a6c-96b0-4f51-af8f-3aa63c575140",
        "primary_pipeline": "e2a51517-5837-44d9-8ea3-45c361aaeeb8",
        "pipelines": [
            {
                "id": "e2a51517-5837-44d9-8ea3-45c361aaeeb8",
                "nodes": [
                    {
                        "id": "595e5a7f-726d-47c3-9fcd-3f8586d6794a",
                        "type": "execution_node",
                        "op": "ingest_cpd_local",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#b28600",
                                "cardDescription": "Ingest data"
                            },
                            "ui_data": {
                                "label": "Load documents",
                                "image": "",
                                "x_pos": 52,
                                "y_pos": 108.80000000000001,
                                "description": "Select documents from your project that you want to process. Supported file types are .pdf, .md, and .txt."
                            }
                        },
                        "outputs": [
                            {
                                "id": "load_documents_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ],
                        "parameters": {
                            "cp4d_asset_ids": [],
                            "cp4d_project_id": "",
                            "input_assets": [
                                {
                                }
                            ]
                        }
                    },
                    {
                        "id": "74ea80e5-0a09-400c-853a-344575ab5700",
                        "type": "execution_node",
                        "op": "extract_cpd",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#00539a",
                                "cardDescription": "Extract data"
                            },
                            "ui_data": {
                                "label": "Extract data",
                                "image": "",
                                "x_pos": 364,
                                "y_pos": 108.80000000000001,
                                "description": "Extract data from the data source to markdown format for further processing."
                            }
                        },
                        "inputs": [
                            {
                                "id": "extract_data_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "30f81035-f825-46b7-8990-b0a1022d576a",
                                        "node_id_ref": "595e5a7f-726d-47c3-9fcd-3f8586d6794a",
                                        "port_id_ref": "load_documents_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "extract_data_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "f5b71605-e78b-4d60-b8b8-7259c3e2e30d",
                        "type": "execution_node",
                        "op": "doc_quality",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#491d8b",
                                "cardDescription": "Quality"
                            },
                            "ui_data": {
                                "label": "Document quality",
                                "image": "",
                                "x_pos": 676,
                                "y_pos": 108.80000000000001,
                                "description": "Analyzes a document for its quality and suitability for ingesting into language models."
                            }
                        },
                        "inputs": [
                            {
                                "id": "document_quality_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "c1145cf4-6e23-4813-b2c4-7ed224e8b91d",
                                        "node_id_ref": "74ea80e5-0a09-400c-853a-344575ab5700",
                                        "port_id_ref": "extract_data_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "document_quality_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "3c5135a4-7016-4fa0-9498-3bb1b3a159fb",
                        "type": "execution_node",
                        "op": "pii_extract_redact",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#491d8b",
                                "cardDescription": "Quality"
                            },
                            "ui_data": {
                                "label": "PII annotator",
                                "image": "",
                                "x_pos": 988,
                                "y_pos": 108.80000000000001,
                                "description": "Identify and annotate personally identifiable information (PII) to maintain data privacy during model ingestion."
                            }
                        },
                        "inputs": [
                            {
                                "id": "pii_annotator_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "6c14b977-7509-408d-be1e-4a4fdf338f82",
                                        "node_id_ref": "f5b71605-e78b-4d60-b8b8-7259c3e2e30d",
                                        "port_id_ref": "document_quality_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "pii_annotator_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "21e19e74-39d0-41fb-a731-56b62cdadcff",
                        "type": "execution_node",
                        "op": "lang_detect",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#491d8b",
                                "cardDescription": "Quality"
                            },
                            "ui_data": {
                                "label": "Language annotator",
                                "image": "",
                                "x_pos": 1300,
                                "y_pos": 108.80000000000001,
                                "description": "Ensure accurate processing by detecting the language of documents before ingestion into the language model."
                            }
                        },
                        "inputs": [
                            {
                                "id": "language_filter_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "27d5bbbc-b9dc-4614-b69e-701e7272984f",
                                        "node_id_ref": "3c5135a4-7016-4fa0-9498-3bb1b3a159fb",
                                        "port_id_ref": "pii_annotator_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "language_filter_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "ea9eff9e-1582-46aa-adb3-58fb8a7870d3",
                        "type": "execution_node",
                        "op": "sql_filter",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#491d8b",
                                "cardDescription": "Quality"
                            },
                            "ui_data": {
                                "label": "Annotation filter",
                                "image": "",
                                "x_pos": 104,
                                "y_pos": 285.6,
                                "description": "Filter documents based on added annotations to streamline processing and ensure relevant content is ingested into the language model.",
                                "ui_parameters": {
                                    "properties": {
                                        "dynamic_available_features_table": [
                                            [
                                                "size"
                                            ],
                                            [
                                                "created_time"
                                            ],
                                            [
                                                "modified_time"
                                            ],
                                            [
                                                "docq_total_words"
                                            ],
                                            [
                                                "docq_mean_word_len"
                                            ],
                                            [
                                                "docq_symbol_to_word_ratio"
                                            ],
                                            [
                                                "docq_sentence_count"
                                            ],
                                            [
                                                "docq_lorem_ipsum_ratio"
                                            ],
                                            [
                                                "docq_contain_bad_word"
                                            ],
                                            [
                                                "docq_bullet_point_ratio"
                                            ],
                                            [
                                                "docq_curly_bracket_ratio"
                                            ],
                                            [
                                                "docq_ellipsis_line_ratio"
                                            ],
                                            [
                                                "docq_alphabet_word_ratio"
                                            ],
                                            [
                                                "docq_contain_common_en_words"
                                            ],
                                            [
                                                "pii_bank_account"
                                            ],
                                            [
                                                "pii_credit_card"
                                            ],
                                            [
                                                "pii_email_address"
                                            ],
                                            [
                                                "pii_ip_address"
                                            ],
                                            [
                                                "pii_phone_number"
                                            ],
                                            [
                                                "pii_ssn_details"
                                            ],
                                            [
                                                "lang_name"
                                            ],
                                            [
                                                "lang_score"
                                            ]
                                        ],
                                        "criteria_list": [
                                            "size > 1000"
                                        ],
                                        "logical_operator": "And",
                                        "columns_to_drop": []
                                    },
                                    "messages": {}
                                }
                            }
                        },
                        "inputs": [
                            {
                                "id": "annotation_filter_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "d8eb0019-3d2c-4c82-94f6-22195896d597",
                                        "node_id_ref": "21e19e74-39d0-41fb-a731-56b62cdadcff",
                                        "port_id_ref": "language_filter_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "annotation_filter_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ],
                        "parameters": {
                            "dynamic_available_features_table": [
                                [
                                    "size"
                                ],
                                [
                                    "created_time"
                                ],
                                [
                                    "modified_time"
                                ],
                                [
                                    "docq_total_words"
                                ],
                                [
                                    "docq_mean_word_len"
                                ],
                                [
                                    "docq_symbol_to_word_ratio"
                                ],
                                [
                                    "docq_sentence_count"
                                ],
                                [
                                    "docq_lorem_ipsum_ratio"
                                ],
                                [
                                    "docq_contain_bad_word"
                                ],
                                [
                                    "docq_bullet_point_ratio"
                                ],
                                [
                                    "docq_curly_bracket_ratio"
                                ],
                                [
                                    "docq_ellipsis_line_ratio"
                                ],
                                [
                                    "docq_alphabet_word_ratio"
                                ],
                                [
                                    "docq_contain_common_en_words"
                                ],
                                [
                                    "pii_bank_account"
                                ],
                                [
                                    "pii_credit_card"
                                ],
                                [
                                    "pii_email_address"
                                ],
                                [
                                    "pii_ip_address"
                                ],
                                [
                                    "pii_phone_number"
                                ],
                                [
                                    "pii_ssn_details"
                                ],
                                [
                                    "lang_name"
                                ],
                                [
                                    "lang_score"
                                ]
                            ],
                            "criteria_list": [
                               
                            ],
                            "logical_operator": "And",
                            "columns_to_drop": []
                        }
                    },
                    {
                        "id": "c7b3c328-e365-4d0e-8c22-980a550ecee7",
                        "type": "execution_node",
                        "op": "chunker",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#520408",
                                "cardDescription": "Transform data"
                            },
                            "ui_data": {
                                "label": "Chunking",
                                "image": "",
                                "x_pos": 364,
                                "y_pos": 299.20000000000005,
                                "description": "Divide text into meaningful sections based on semantic content, improving context understanding and processing accuracy."
                            }
                        },
                        "inputs": [
                            {
                                "id": "chunking_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "c5466854-68f1-47d7-88bd-246f59ee119b",
                                        "node_id_ref": "ea9eff9e-1582-46aa-adb3-58fb8a7870d3",
                                        "port_id_ref": "annotation_filter_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "chunking_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "dcdcf527-3360-4a3a-90e0-bcc70a455760",
                        "type": "execution_node",
                        "op": "embeddings",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#520408",
                                "cardDescription": "Transform data"
                            },
                            "ui_data": {
                                "label": "Embeddings",
                                "image": "",
                                "x_pos": 624,
                                "y_pos": 299.20000000000005,
                                "description": "Generate embeddings to transform text into numerical vectors."
                            }
                        },
                        "inputs": [
                            {
                                "id": "embeddings_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "032dba91-5cbf-4bef-be15-dc4de7b49e16",
                                        "node_id_ref": "c7b3c328-e365-4d0e-8c22-980a550ecee7",
                                        "port_id_ref": "chunking_outPort"
                                    }
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "id": "embeddings_outPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Output Port"
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "id": "49f7ca63-ab12-4309-8f25-c62721309dad",
                        "type": "execution_node",
                        "op": "milvusdb_cp4d",
                        "app_data": {
                            "react_nodes_data": {
                                "color": "#009d9a",
                                "cardDescription": "Generate output"
                            },
                            "ui_data": {
                                "label": "watsonx.data Milvus",
                                "image": "",
                                "x_pos": 884,
                                "y_pos": 299.20000000000005,
                                "description": "Load embeddings into watsonx.data to integrate and manage vector data efficiently.",
                                "ui_parameters": {
                                    "properties": {
                                        "connection_id": "797a47b3-6ea3-430f-ae4c-4c965e916af7",
                                        "output_connection": {
                                            "connection_id": "797a47b3-6ea3-430f-ae4c-4c965e916af7",
                                            "connection_name": "Milvus Exrernal connection"
                                        },
                                        "selected_connection": [
                                            "Milvus Exrernal connection"
                                        ],
                                        "collection_name": "udp_lf_py_all_10dec743pm_db"
                                    },
                                    "messages": {}
                                }
                            }
                        },
                        "inputs": [
                            {
                                "id": "watsonx_data_inPort",
                                "app_data": {
                                    "ui_data": {
                                        "cardinality": {
                                            "min": 1,
                                            "max": 1
                                        },
                                        "label": "Input Port"
                                    }
                                },
                                "links": [
                                    {
                                        "id": "2636b671-aa59-4ed1-b97c-0d517b53616d",
                                        "node_id_ref": "dcdcf527-3360-4a3a-90e0-bcc70a455760",
                                        "port_id_ref": "embeddings_outPort"
                                    }
                                ]
                            }
                        ],
                        "parameters": {
                            "connection_id": "",
                            "output_connection": {
                                "connection_id": "",
                                "connection_name": ""
                            },
                            "collection_name": ""
                        }
                    }
                ],
                "app_data": {
                    "ds_flow": {
                        "name": "My Datasift Flow",
                        "description": "Detailed description of the flow",
                        "job_name": "My Datasift job",
                        "schedule": {},
                        "global_config": {
                            "doc_column": "content",
                            "data_local_config": {
                                "output_folder": "./test/flows/output"
                            },
                            "data_storage_type": "local"
                        }
                    },
                    "ui_data": {
                        "comments": []
                    }
                },
                "runtime_ref": ""
            }
        ],
        "schemas": []
    }
}