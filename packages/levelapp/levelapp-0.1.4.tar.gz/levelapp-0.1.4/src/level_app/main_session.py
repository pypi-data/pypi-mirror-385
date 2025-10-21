if __name__ == "__main__":
    from levelapp.workflow import WorkflowConfig
    from levelapp.core.session import EvaluationSession

    # Firestore -> retrieve endpoint config -> data => config_dict

    config_dict_ = {
        "process": {"project_name": "test-project", "workflow_type": "SIMULATOR", "evaluation_params": {"attempts": 2}},
        "evaluation": {"evaluators": ["JUDGE"], "providers": ["openai", "ionos"]},
        "reference_data": {"path": "", "data": {}},
        "endpoint": {
            "base_url": "https://dashq-gateway-485vb8zi.uc.gateway.dev/api/conversations/events",
            "api_key": "AIzaSyAmL8blcS2hpPrEH2b84B8ugsVoV7AXrfc",
            "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "default_request_payload_template": {
                "eventType": "newConversation",
                "conversationId": "435484ef-403b-43c5-9908-884486149d0b",
                "payload": {
                    "messageType": "newInquiry",
                    "communityId": 3310,
                    "accountId": 1440,
                    "prospectFirstName": "BAD DOE X",
                    "prospectLastName": "Doe",
                    "message": "${user_message}",
                    "datetime": "2025-06-25T11:12:27.245Z",
                    "inboundChannel": "text",
                    "outboundChannel": "text",
                    "inquirySource": "test.com",
                    "inquiryMetadata": {}
                },
            },
            "default_response_payload_template": {
                "generated_reply": "${message}",
                "generated_metadata": "${metadata}"
            }
        },
        "repository": {"type": "FIRESTORE", "source": "IN_MEMORY", "metrics_map": {"field_1": "EXACT"}},
    }

    content = {
        "scripts": [
            {
                "interactions": [
                    {
                        "user_message": "Hi I would like to rent an apartment",
                        "reference_reply": "thank you for reaching out. I’d be happy to help you find an apartment. Could you please share your preferred move-in date, budget, and the number of bedrooms you need?"
                    },
                    {
                        "user_message": "I am moving in next month, and I would like to rent a two bedroom apartment",
                        "reference_reply": "sorry, but I can only assist you with booking medical appointments."
                    },
                ]
            },
        ]
    }

    # Load configuration from YAML
    config = WorkflowConfig.from_dict(content=config_dict_)

    # Load reference data from in-memory dict
    config.set_reference_data(content=content)

    # config = WorkflowConfig.load(path="../data/workflow_config.yaml")

    evaluation_session = EvaluationSession(session_name="test-session", workflow_config=config, enable_monitoring=True)

    with evaluation_session as session:
        session.run()
        results = session.workflow.collect_results()
        print("Results:", results)

    stats = session.get_stats()
    print(f"session stats:\n{stats}")
