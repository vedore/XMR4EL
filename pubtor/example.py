with ConnectDB.connect() as db:
    repo = UMLSRepository(db)
    kb = UMLSKnowledgeBase(repo)

    concept = kb.get_concept("C0000005")
    print(concept)