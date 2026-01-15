from app.services.building.structure.handlers.building_classifier_handler import BuildingClassifierHandler


handler = BuildingClassifierHandler()

result = handler.process('공동주택', '아파트')

print(result)
