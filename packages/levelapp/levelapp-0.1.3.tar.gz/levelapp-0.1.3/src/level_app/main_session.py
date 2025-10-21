if __name__ == "__main__":
    from levelapp.workflow import WorkflowConfig
    from levelapp.core.session import EvaluationSession

    # Firestore -> retrieve endpoint config -> data => config_dict

    # config_dict_ = {
    #     "process": {"project_name": "test-project", "workflow_type": "SIMULATOR", "evaluation_params": {"attempts": 2}},
    #     "evaluation": {"evaluators": ["JUDGE"], "providers": ["openai", "ionos"]},
    #     "reference_data": {"path": "", "data": {}},
    #     "endpoint": {"base_url": "http://127.0.0.1:8000", "api_key": "key", "model_id": "model"},
    #     "repository": {"type": "FIRESTORE", "source": "IN_MEMORY", "metrics_map": {"field_1": "EXACT"}},
    # }
    #
    # content = {
    #     "scripts": [
    #         {
    #             "interactions": [
    #                 {
    #                     "user_message": "Hello World!",
    #                     "reference_reply": "Hello, how can I help you!"
    #                 },
    #                 {
    #                     "user_message": "I need an apartment",
    #                     "reference_reply": "sorry, but I can only assist you with booking medical appointments."
    #                 },
    #             ]
    #         },
    #     ]
    # }
    #
    # # Load configuration from YAML
    # config = WorkflowConfig.from_dict(content=config_dict_)
    #
    # # Load reference data from in-memory dict
    # config.set_reference_data(content=content)

    config = WorkflowConfig.load(path="../data/workflow_config.yaml")

    evaluation_session = EvaluationSession(session_name="test-session", workflow_config=config, enable_monitoring=True)

    with evaluation_session as session:
        session.run()
        results = session.workflow.collect_results()
        print("Results:", results)

    stats = session.get_stats()
    print(f"session stats:\n{stats}")
