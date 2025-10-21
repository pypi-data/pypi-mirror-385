# # test_mixins.py

# from draftsman.classes.blueprint import Blueprint
# from draftsman.classes.vector import Vector
# from draftsman.constants import *
# from draftsman.entity import *
# from draftsman.error import *
# from draftsman.signatures import RequestFilters, SignalID
# from draftsman.warning import *

# import pytest


# class TestCircuitConditionMixin:
#     def test_set_enable_disable(self):
#         transport_belt = TransportBelt()
#         transport_belt.enable_disable = True
#         assert transport_belt.enable_disable == True
#         assert transport_belt.control_behavior == {"circuit_enable_disable": True}

#         transport_belt.enable_disable = None
#         assert transport_belt.control_behavior == {}

#         with pytest.raises(TypeError):
#             transport_belt.enable_disable = "True"

#     def test_set_circuit_condition(self):
#         transport_belt = TransportBelt()
#         # Valid
#         transport_belt.set_circuit_condition(None)
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {"comparator": "<", "constant": 0}
#         }
#         transport_belt.set_circuit_condition("signal-A", ">", -10)
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": ">",
#                 "constant": -10,
#             }
#         }
#         transport_belt.set_circuit_condition("signal-A", "==", -10)
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": "=",
#                 "constant": -10,
#             }
#         }
#         transport_belt.set_circuit_condition("signal-A", "<=", "signal-B")
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": "≤",
#                 "second_signal": {"name": "signal-B", "type": "virtual"},
#             }
#         }
#         transport_belt.set_circuit_condition("signal-A", "≤", "signal-B")
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": "≤",
#                 "second_signal": {"name": "signal-B", "type": "virtual"},
#             }
#         }
#         transport_belt.set_circuit_condition("signal-A", "!=", "signal-B")
#         assert transport_belt.control_behavior == {
#             "circuit_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": "≠",
#                 "second_signal": {"name": "signal-B", "type": "virtual"},
#             }
#         }

#         # Errors
#         # Constant first
#         with pytest.raises(DataFormatError):
#             transport_belt.set_circuit_condition(10, ">", "signal-B")
#         # Invalid A
#         with pytest.raises(DataFormatError):
#             transport_belt.set_circuit_condition(TypeError, ">", "signal-B")
#         # Invalid Operation
#         with pytest.raises(DataFormatError):
#             transport_belt.set_circuit_condition("signal-A", "hmm", "signal-B")
#         # Invalid B
#         with pytest.raises(DataFormatError):
#             transport_belt.set_circuit_condition("signal-A", ">", TypeError)

#     def test_remove_circuit_condition(self):  # TODO delete
#         transport_belt = TransportBelt()
#         transport_belt.set_circuit_condition(None)
#         transport_belt.remove_circuit_condition()
#         assert transport_belt.control_behavior == {}

#     def test_normalize_circuit_condition(self):  # TODO delete
#         transport_belt = TransportBelt(control_behavior={})
#         assert transport_belt.to_dict() == {
#             "name": "transport-belt",
#             "position": {"x": 0.5, "y": 0.5},
#         }
#         transport_belt = TransportBelt(control_behavior={"circuit_condition": {}})
#         assert transport_belt.to_dict() == {
#             "name": "transport-belt",
#             "position": {"x": 0.5, "y": 0.5},
#             "control_behavior": {"circuit_condition": {}},
#         }
#         transport_belt = TransportBelt(
#             control_behavior={
#                 "circuit_condition": {
#                     "first_signal": {"name": "signal-A", "type": "virtual"},
#                     "second_signal": {"name": "signal-B", "type": "virtual"},
#                 }
#             }
#         )
#         assert transport_belt.to_dict() == {
#             "name": "transport-belt",
#             "position": {"x": 0.5, "y": 0.5},
#             "control_behavior": {
#                 "circuit_condition": {
#                     "first_signal": {"name": "signal-A", "type": "virtual"},
#                     "second_signal": {"name": "signal-B", "type": "virtual"},
#                 }
#             },
#         }


# ################################################################################


# class TestCircuitConnectableMixin:
#     pass


# ################################################################################


# class TestCircuitReadContentsMixin:
#     def test_set_read_contents(self):
#         transport_belt = TransportBelt()
#         transport_belt.read_contents = True
#         assert transport_belt.read_contents == True
#         assert transport_belt.control_behavior == {"circuit_read_hand_contents": True}
#         transport_belt.read_contents = None
#         assert transport_belt.control_behavior == {}

#         with pytest.raises(TypeError):
#             transport_belt.read_contents = "wrong"

#     def test_set_read_mode(self):
#         transport_belt = TransportBelt()
#         # transport_belt.set_read_mode(ReadMode.HOLD)
#         transport_belt.read_mode = ReadMode.HOLD
#         assert transport_belt.read_mode == ReadMode.HOLD
#         assert transport_belt.control_behavior == {"circuit_contents_read_mode": 1}
#         # transport_belt.set_read_mode(None)
#         transport_belt.read_mode = None
#         assert transport_belt.control_behavior == {}

#         with pytest.raises(ValueError):
#             transport_belt.read_mode = "wrong"


# ################################################################################


# class TestCircuitReadHandMixin:
#     def test_set_read_contents(self):
#         inserter = Inserter()
#         inserter.read_hand_contents = True
#         assert inserter.read_hand_contents == True
#         assert inserter.control_behavior == {"circuit_read_hand_contents": True}
#         inserter.read_hand_contents = None
#         assert inserter.control_behavior == {}

#         with pytest.raises(TypeError):
#             inserter.read_hand_contents = "wrong"

#     def test_set_read_mode(self):
#         inserter = Inserter()
#         inserter.read_mode = ReadMode.HOLD
#         assert inserter.read_mode == ReadMode.HOLD
#         assert inserter.control_behavior == {"circuit_hand_read_mode": 1}
#         inserter.read_mode = None
#         assert inserter.control_behavior == {}

#         with pytest.raises(ValueError):
#             inserter.read_mode = "wrong"


# ################################################################################


# class TestCircuitReadResourceMixin:
#     def test_set_read_resources(self):
#         pass

#     def test_set_read_mode(self):
#         pass


# ################################################################################


# class TestColorMixin:
#     def test_set_color(self):
#         train_stop = TrainStop()
#         # Valid 4 args
#         train_stop.color = (0.1, 0.1, 0.1, 0.1)
#         assert train_stop.color == (0.1, 0.1, 0.1, 0.1)
#         assert train_stop.to_dict()["color"] == {"r": 0.1, "g": 0.1, "b": 0.1, "a": 0.1}
#         # Valid 3 args
#         train_stop.color = (0.1, 0.1, 0.1)
#         assert train_stop.color == (0.1, 0.1, 0.1)
#         assert train_stop.to_dict()["color"] == {"r": 0.1, "g": 0.1, "b": 0.1}
#         # None
#         train_stop.color = None
#         assert train_stop.color == None

#         # TODO: move to validate
#         # with pytest.raises(DataFormatError):
#         #     train_stop.color = (1000, 200, 0)

#         # with pytest.raises(DataFormatError):
#         #     train_stop.color = ("wrong", 1.0, 1.0)


# ################################################################################


# class TestControlBehaviorMixin:
#     def test_set_control_behavior(self):
#         combinator = ArithmeticCombinator()
#         combinator.control_behavior = None
#         assert combinator.control_behavior == {}


# ################################################################################


# class TestDirectionalMixin:
#     def test_set_direction(self):
#         storage_tank = StorageTank()
#         storage_tank.direction = Direction.SOUTH
#         assert storage_tank.direction == Direction.SOUTH
#         # Default testing
#         storage_tank.direction = Direction.NORTH
#         assert storage_tank.direction == Direction.NORTH
#         assert storage_tank.to_dict() == {
#             "name": storage_tank.name,
#             "position": storage_tank.position.to_dict(),
#         }
#         storage_tank.direction = None
#         assert storage_tank.direction == 0
#         assert storage_tank.to_dict() == {
#             "name": storage_tank.name,
#             "position": storage_tank.position.to_dict(),
#         }
#         # Warnings
#         with pytest.warns(DirectionWarning):
#             storage_tank.direction = Direction.NORTHEAST
#         # Errors
#         with pytest.raises(ValueError):
#             storage_tank.direction = "1000"

#         blueprint = Blueprint()
#         blueprint.entities.append("flamethrower-turret")
#         with pytest.raises(
#             DraftsmanError,
#             match="Cannot set this direction of non-square entity while it's in another object; might intersect neighbours",
#         ):
#             blueprint.entities[0].direction = Direction.EAST

#     def test_set_position(self):
#         storage_tank = StorageTank()
#         storage_tank.position = (1.23, 1.34)
#         assert storage_tank.position == Vector(1.23, 1.34)
#         assert storage_tank.position.to_dict() == {"x": 1.23, "y": 1.34}
#         target_pos = Vector(
#             round(storage_tank.position.x - storage_tank.tile_width / 2.0),
#             round(storage_tank.position.y - storage_tank.tile_height / 2.0),
#         )
#         assert storage_tank.tile_position == target_pos

#         with pytest.raises(ValueError):
#             storage_tank.position = ("fish", 10)

#         storage_tank.tile_position = (10, 10.1)  # should cast float to int
#         assert storage_tank.tile_position == Vector(10, 10)
#         assert storage_tank.tile_position.to_dict() == {"x": 10, "y": 10}
#         target_pos = Vector(
#             storage_tank.tile_position.x + storage_tank.tile_width / 2.0,
#             storage_tank.tile_position.y + storage_tank.tile_height / 2.0,
#         )
#         assert storage_tank.position == target_pos

#         with pytest.raises(ValueError):
#             storage_tank.position = (1.0, "raw-fish")


# ################################################################################


# class TestDoubleGridAlignedMixin:
#     def test_set_absolute_position(self):
#         rail = StraightRail()
#         assert rail.position == Vector(1.0, 1.0)
#         assert rail.position.to_dict() == {"x": 1.0, "y": 1.0}
#         assert rail.tile_position == Vector(0, 0)
#         assert rail.tile_position.to_dict() == {"x": 0, "y": 0}
#         assert rail.double_grid_aligned == True
#         with pytest.warns(GridAlignmentWarning):
#             rail.position = (2.0, 2.0)


# ################################################################################


# class TestEightWayDirectionalMixin:
#     def test_set_direction(self):
#         rail = StraightRail()
#         rail.direction = 6
#         assert rail.direction == Direction.WEST
#         rail.direction = None
#         assert rail.direction == Direction.NORTH
#         with pytest.raises(ValueError):
#             rail.direction = ValueError


# ################################################################################


# class TestFiltersMixin:
#     def test_set_item_filter(self):
#         inserter = FilterInserter()

#         inserter.set_item_filter(0, "small-lamp")
#         assert inserter.filters == [{"index": 1, "name": "small-lamp"}]
#         inserter.set_item_filter(1, "burner-inserter")
#         assert inserter.filters == [
#             {"index": 1, "name": "small-lamp"},
#             {"index": 2, "name": "burner-inserter"},
#         ]

#         inserter.set_item_filter(0, "fast-transport-belt")
#         assert inserter.filters == [
#             {"index": 1, "name": "fast-transport-belt"},
#             {"index": 2, "name": "burner-inserter"},
#         ]

#         inserter.set_item_filter(0, None)
#         assert inserter.filters == [{"index": 2, "name": "burner-inserter"}]

#         # Errors
#         with pytest.raises(IndexError):
#             inserter.set_item_filter(100, "small-lamp")

#         with pytest.raises(InvalidItemError):
#             inserter.set_item_filter(0, "incorrect")

#     def test_set_item_filters(self):
#         inserter = FilterInserter()

#         inserter.set_item_filters(
#             ["transport-belt", "fast-transport-belt", "express-transport-belt"]
#         )
#         assert inserter.filters == [
#             {"index": 1, "name": "transport-belt"},
#             {"index": 2, "name": "fast-transport-belt"},
#             {"index": 3, "name": "express-transport-belt"},
#         ]

#         inserter.set_item_filters(
#             [
#                 {"index": 1, "name": "transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#                 {"index": 3, "name": "express-transport-belt"},
#             ]
#         )
#         assert inserter.filters == [
#             {"index": 1, "name": "transport-belt"},
#             {"index": 2, "name": "fast-transport-belt"},
#             {"index": 3, "name": "express-transport-belt"},
#         ]

#         inserter.set_item_filters(None)
#         assert inserter.filters == None

#         # Errors
#         with pytest.raises(DataFormatError):
#             inserter.set_item_filters({"incorrect": "format"})

#         with pytest.raises(IndexError):
#             inserter.set_item_filters(
#                 [
#                     {"index": 1, "name": "transport-belt"},
#                     {"index": 100, "name": "fast-transport-belt"},
#                     {"index": 3, "name": "express-transport-belt"},
#                 ]
#             )

#         with pytest.raises(InvalidItemError):
#             inserter.set_item_filters(
#                 ["transport-belt", "incorrect", "express-transport-belt"]
#             )

#         with pytest.raises(InvalidItemError):
#             inserter.set_item_filters(
#                 [
#                     {"index": 1, "name": "transport-belt"},
#                     {"index": 2, "name": "incorrect"},
#                     {"index": 3, "name": "express-transport-belt"},
#                 ]
#             )


# ################################################################################


# class TestInfinitySettingsMixin:
#     def test_set_infinity_settings(self):
#         pass


# ################################################################################


# class TestInventoryMixin:
#     def test_bar_index(self):
#         container = Container("wooden-chest")
#         # TODO: move to inspect
#         # with pytest.warns(IndexWarning):
#         #     for i in range(container.inventory_size + 1):
#         #         container.bar = i

#         # None case
#         container.bar = None
#         assert container.bar == None

#         # TODO: move to validate
#         # with pytest.raises(IndexError):
#         #     container.bar = -1

#         # with pytest.raises(IndexError):
#         #     container.bar = 100000000  # 100,000,000

#         # with pytest.raises(TypeError):
#         #     container.bar = "lmao a string! Who'd do such a dastardly thing????"


# ################################################################################


# class TestInventoryFilterMixin:
#     def test_set_inventory(self):
#         cargo_wagon = CargoWagon("cargo-wagon")
#         cargo_wagon.inventory = None
#         assert cargo_wagon.inventory == {}

#     def test_set_inventory_filter(self):
#         cargo_wagon = CargoWagon("cargo-wagon")
#         cargo_wagon.set_inventory_filter(0, "transport-belt")
#         assert cargo_wagon.inventory == {
#             "filters": [{"index": 1, "name": "transport-belt"}]
#         }
#         cargo_wagon.set_inventory_filter(1, "fast-transport-belt")
#         assert cargo_wagon.inventory == {
#             "filters": [
#                 {"index": 1, "name": "transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#             ]
#         }
#         cargo_wagon.set_inventory_filter(0, "express-transport-belt")
#         assert cargo_wagon.inventory == {
#             "filters": [
#                 {"index": 1, "name": "express-transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#             ]
#         }
#         cargo_wagon.set_inventory_filter(0, None)
#         assert cargo_wagon.inventory == {
#             "filters": [{"index": 2, "name": "fast-transport-belt"}]
#         }

#         # Errors
#         with pytest.raises(ValueError):
#             cargo_wagon.set_inventory_filter("double", "incorrect")
#         with pytest.raises(InvalidItemError):
#             cargo_wagon.set_inventory_filter(0, "incorrect")
#         with pytest.raises(IndexError):
#             cargo_wagon.set_inventory_filter(50, "stone")

#     def test_set_inventory_filters(self):
#         cargo_wagon = CargoWagon("cargo-wagon")
#         cargo_wagon.set_inventory_filters(["transport-belt", "fast-transport-belt"])
#         assert cargo_wagon.inventory == {
#             "filters": [
#                 {"index": 1, "name": "transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#             ]
#         }
#         cargo_wagon.set_inventory_filters(
#             [
#                 {"index": 1, "name": "express-transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#             ]
#         )
#         assert cargo_wagon.inventory == {
#             "filters": [
#                 {"index": 1, "name": "express-transport-belt"},
#                 {"index": 2, "name": "fast-transport-belt"},
#             ]
#         }
#         cargo_wagon.set_inventory_filters(None)
#         assert cargo_wagon.inventory == {}

#         # Warnings
#         # Warn if index is out of range
#         # TODO

#         # Errors
#         # TODO: reinstate
#         with pytest.raises(DataFormatError):
#             cargo_wagon.set_inventory_filters(TypeError)

#         with pytest.raises(InvalidItemError):
#             cargo_wagon.set_inventory_filters(["incorrect1", "incorrect2"])

#     def test_set_bar_index(self):
#         cargo_wagon = CargoWagon()
#         cargo_wagon.bar = 10
#         assert cargo_wagon.bar == 10
#         assert cargo_wagon.inventory == {"bar": 10}
#         cargo_wagon.bar = None
#         assert cargo_wagon.inventory == {}

#         # Warnings
#         # Out of index range warning
#         with pytest.warns(IndexWarning):
#             cargo_wagon.bar = 100

#         # Errors
#         with pytest.raises(TypeError):
#             cargo_wagon.bar = "incorrect"

#         with pytest.raises(IndexError):
#             cargo_wagon.bar = -1

#         with pytest.raises(IndexError):
#             cargo_wagon.bar = 100000000  # 100,000,000


# ################################################################################


# class TestIOTypeMixin:
#     def test_set_io_type(self):
#         belt = UndergroundBelt()
#         # belt.io_type = "input"

#         with pytest.raises(TypeError):
#             belt.io_type = TypeError

#         with pytest.raises(ValueError):
#             belt.io_type = "not correct"


# ################################################################################


# class TestLogisticConditionMixin:
#     def test_connect_to_logistic_network(self):
#         transport_belt = TransportBelt()
#         transport_belt.connect_to_logistic_network = True
#         assert transport_belt.connect_to_logistic_network == True
#         assert transport_belt.control_behavior == {"connect_to_logistic_network": True}

#         transport_belt.connect_to_logistic_network = None
#         assert transport_belt.control_behavior == {}

#         with pytest.raises(TypeError):
#             transport_belt.connect_to_logistic_network = "True"

#     def test_set_logistic_condition(self):
#         transport_belt = TransportBelt()
#         # Valid
#         transport_belt.set_logistic_condition(None)
#         assert transport_belt.control_behavior == {
#             "logistic_condition": {"comparator": "<", "constant": 0}
#         }
#         transport_belt.set_logistic_condition("signal-A", ">", -10)
#         assert transport_belt.control_behavior == {
#             "logistic_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": ">",
#                 "constant": -10,
#             }
#         }
#         transport_belt.set_logistic_condition("signal-A", "<=", "signal-B")
#         assert transport_belt.control_behavior == {
#             "logistic_condition": {
#                 "first_signal": {"name": "signal-A", "type": "virtual"},
#                 "comparator": "≤",
#                 "second_signal": {"name": "signal-B", "type": "virtual"},
#             }
#         }

#         # Errors
#         # Constant first
#         with pytest.raises(DataFormatError):
#             transport_belt.set_logistic_condition(10, ">", "signal-B")
#         # Invalid A
#         with pytest.raises(DataFormatError):
#             transport_belt.set_logistic_condition(TypeError, ">", "signal-B")
#         # Invalid Operation
#         with pytest.raises(DataFormatError):
#             transport_belt.set_logistic_condition("signal-A", "hmm", "signal-B")
#         # Invalid B
#         with pytest.raises(DataFormatError):
#             transport_belt.set_logistic_condition("signal-A", ">", TypeError)

#     def test_remove_logistic_condition(self):  # TODO delete
#         transport_belt = TransportBelt()
#         transport_belt.set_logistic_condition(None)
#         transport_belt.remove_logistic_condition()
#         assert transport_belt.control_behavior == {}


# ################################################################################


# class TestInserterModeOfOperationMixin:
#     def test_set_mode_of_operation(self):
#         inserter = Inserter()
#         inserter.mode_of_operation = None
#         assert inserter.mode_of_operation == None
#         assert inserter.control_behavior == {}
#         # Default
#         inserter.mode_of_operation = InserterModeOfOperation.ENABLE_DISABLE
#         assert inserter.control_behavior == {
#             "circuit_mode_of_operation": InserterModeOfOperation.ENABLE_DISABLE
#         }
#         inserter.mode_of_operation = InserterModeOfOperation.NONE
#         assert inserter.control_behavior == {
#             "circuit_mode_of_operation": InserterModeOfOperation.NONE
#         }
#         # Errors
#         with pytest.raises(ValueError):
#             inserter.mode_of_operation = "wrong"


# ################################################################################


# class TestLogisticModeOfOperationMixin:
#     def test_set_mode_of_operation(self):
#         requester = LogisticRequestContainer()
#         requester.mode_of_operation = None
#         assert requester.mode_of_operation == None
#         assert requester.control_behavior == {}
#         # Default
#         requester.mode_of_operation = LogisticModeOfOperation.SEND_CONTENTS
#         assert requester.control_behavior == {
#             "circuit_mode_of_operation": LogisticModeOfOperation.SEND_CONTENTS
#         }
#         requester.mode_of_operation = LogisticModeOfOperation.SET_REQUESTS
#         assert requester.control_behavior == {
#             "circuit_mode_of_operation": LogisticModeOfOperation.SET_REQUESTS
#         }
#         # Errors
#         with pytest.raises(ValueError):
#             requester.mode_of_operation = "wrong"


# ################################################################################


# class TestOrientationMixin:
#     def test_set_orientation(self):
#         locomotive = Locomotive()
#         locomotive.orientation = 0.25
#         assert locomotive.to_dict() == {
#             "name": "locomotive",
#             "position": {"x": 1.0, "y": 3.0},
#             "orientation": 0.25,
#         }
#         locomotive.orientation = None
#         assert locomotive.orientation == 0.0

#         locomotive.orientation = 2.5
#         assert locomotive.orientation == 0.5

#         with pytest.raises(TypeError):
#             locomotive.orientation = "incorrect"


# ################################################################################


# class TestPowerConnectableMixin:
#     def test_set_neighbours(self):
#         substation = ElectricPole("substation")
#         substation.neighbours = None
#         assert substation.neighbours == []
#         # TODO: move to validate
#         # with pytest.raises(DataFormatError):
#         #     substation.neighbours = {"completely", "wrong"}

#     # def test_add_power_connection(self):
#     #     substation1 = ElectricPole("substation", id="1")
#     #     substation2 = ElectricPole("substation", id="2")
#     #     power_switch = PowerSwitch(id="p")

#     #     substation1.add_power_connection(substation2)
#     #     self.assertEqual(substation1.neighbours, ["2"])
#     #     self.assertEqual(substation2.neighbours, ["1"])
#     #     substation2.add_power_connection(substation1)
#     #     self.assertEqual(substation1.neighbours, ["2"])
#     #     self.assertEqual(substation2.neighbours, ["1"])

#     #     substation1.add_power_connection(power_switch)
#     #     self.assertEqual(substation1.neighbours, ["2"])
#     #     self.assertEqual(
#     #         power_switch.connections, {"Cu0": [{"entity_id": "1", "wire_id": 0}]}
#     #     )
#     #     power_switch.add_power_connection(substation1)
#     #     self.assertEqual(substation1.neighbours, ["2"])
#     #     self.assertEqual(
#     #         power_switch.connections, {"Cu0": [{"entity_id": "1", "wire_id": 0}]}
#     #     )
#     #     substation2.add_power_connection(power_switch)
#     #     substation2.add_power_connection(power_switch)
#     #     self.assertEqual(substation2.neighbours, ["1"])
#     #     self.assertEqual(
#     #         power_switch.connections,
#     #         {
#     #             "Cu0": [
#     #                 {"entity_id": "1", "wire_id": 0},
#     #                 {"entity_id": "2", "wire_id": 0},
#     #             ]
#     #         },
#     #     )
#     #     power_switch.add_power_connection(substation2, side=2)
#     #     self.assertEqual(
#     #         power_switch.connections,
#     #         {
#     #             "Cu0": [
#     #                 {"entity_id": "1", "wire_id": 0},
#     #                 {"entity_id": "2", "wire_id": 0},
#     #             ],
#     #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
#     #         },
#     #     )

#     #     # Warnings
#     #     with self.assertWarns(ConnectionDistanceWarning):
#     #         other = ElectricPole(position=[100, 0], id="other")
#     #         substation1.add_power_connection(other)

#     #     # Errors
#     #     with self.assertRaises(EntityNotPowerConnectableError):
#     #         substation1.add_power_connection(TransportBelt(id="whatever"))
#     #     with self.assertRaises(Exception):
#     #         power_switch.add_power_connection(PowerSwitch())

#     #     # Make sure correct even after errors
#     #     self.assertEqual(substation1.neighbours, ["2", "other"])
#     #     self.assertEqual(
#     #         power_switch.connections,
#     #         {
#     #             "Cu0": [
#     #                 {"entity_id": "1", "wire_id": 0},
#     #                 {"entity_id": "2", "wire_id": 0},
#     #             ],
#     #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
#     #         },
#     #     )

#     #     # Test removing
#     #     substation1.remove_power_connection(substation2)
#     #     substation1.remove_power_connection(substation2)
#     #     self.assertEqual(substation1.neighbours, ["other"])
#     #     self.assertEqual(substation2.neighbours, [])

#     #     substation1.remove_power_connection(power_switch)
#     #     substation1.remove_power_connection(power_switch)
#     #     self.assertEqual(substation1.neighbours, ["other"])
#     #     self.assertEqual(
#     #         power_switch.connections,
#     #         {
#     #             "Cu0": [{"entity_id": "2", "wire_id": 0}],
#     #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
#     #         },
#     #     )

#     #     substation1.add_power_connection(power_switch)
#     #     power_switch.remove_power_connection(substation2, side=1)
#     #     power_switch.remove_power_connection(substation2, side=1)
#     #     power_switch.remove_power_connection(substation1)
#     #     power_switch.remove_power_connection(substation1)
#     #     self.assertEqual(
#     #         power_switch.connections, {"Cu1": [{"entity_id": "2", "wire_id": 0}]}
#     #     )
#     #     substation2.remove_power_connection(power_switch, side=2)
#     #     substation2.remove_power_connection(power_switch, side=2)
#     #     self.assertEqual(power_switch.connections, {})


# ################################################################################


# class TestReadRailSignalMixin:
#     def test_set_output_signals(self):
#         rail_signal = RailSignal()
#         rail_signal.red_output_signal = "signal-A"
#         assert rail_signal.red_output_signal == "signal-A"
#         assert rail_signal.control_behavior == {
#             "red_output_signal": "signal-A"
#         }
#         rail_signal.red_output_signal = {"name": "signal-A", "type": "virtual"}
#         assert rail_signal.control_behavior == {
#             "red_output_signal": {"name": "signal-A", "type": "virtual"}
#         }
#         rail_signal.red_output_signal = None
#         assert rail_signal.control_behavior == {}
#         with pytest.raises(DataFormatError):
#             rail_signal.red_output_signal = TypeError
#         with pytest.raises(InvalidSignalError):
#             rail_signal.red_output_signal = "incorrect"

#         rail_signal.yellow_output_signal = "signal-A"
#         assert rail_signal.yellow_output_signal == "signal-A"
#         assert rail_signal.control_behavior == {
#             "orange_output_signal": "signal-A"
#         }
#         rail_signal.yellow_output_signal = {"name": "signal-A", "type": "virtual"}
#         assert rail_signal.control_behavior == {
#             "orange_output_signal": {"name": "signal-A", "type": "virtual"}
#         }
#         rail_signal.yellow_output_signal = None
#         assert rail_signal.control_behavior == {}
#         with pytest.raises(DataFormatError):
#             rail_signal.yellow_output_signal = TypeError
#         with pytest.raises(InvalidSignalError):
#             rail_signal.yellow_output_signal = "wrong"

#         rail_signal.green_output_signal = "signal-A"
#         assert rail_signal.green_output_signal == "signal-A"
#         assert rail_signal.control_behavior == {
#             "green_output_signal": "signal-A"
#         }
#         rail_signal.green_output_signal = {"name": "signal-A", "type": "virtual"}
#         assert rail_signal.control_behavior == {
#             "green_output_signal": {"name": "signal-A", "type": "virtual"}
#         }
#         rail_signal.green_output_signal = None
#         assert rail_signal.control_behavior == {}
#         with pytest.raises(DataFormatError):
#             rail_signal.green_output_signal = TypeError
#         with pytest.raises(InvalidSignalError):
#             rail_signal.green_output_signal = "mistake"


# ################################################################################


# class TestRecipeMixin:
#     def test_set_recipe(self):
#         machine = AssemblingMachine()

#         with pytest.raises(TypeError):
#             machine.recipe = TypeError


# ################################################################################


# class TestRequestFiltersMixin:
#     def test_set_request_filter(self):
#         storage_chest = LogisticStorageContainer()
#         storage_chest.set_request_filter(0, "stone", 100)
#         assert storage_chest.request_filters == [
#             {"index": 1, "name": "stone", "count": 100}
#         ]
#         storage_chest.set_request_filter(1, "copper-ore", 200)
#         assert storage_chest.request_filters == [
#             {"index": 1, "name": "stone", "count": 100},
#             {"index": 2, "name": "copper-ore", "count": 200},
#         ]
#         storage_chest.set_request_filter(0, "iron-ore", 1000)
#         assert storage_chest.request_filters == [
#             {"index": 1, "name": "iron-ore", "count": 1000},
#             {"index": 2, "name": "copper-ore", "count": 200},
#         ]
#         storage_chest.set_request_filter(0, None)
#         assert storage_chest.request_filters == [
#             {"index": 2, "name": "copper-ore", "count": 200}
#         ]
#         # test default
#         storage_chest.set_request_filter(2, "fast-transport-belt")
#         assert storage_chest.request_filters == [
#             {"index": 2, "name": "copper-ore", "count": 200},
#             {"index": 3, "name": "fast-transport-belt", "count": 100},
#         ]

#         # Errors
#         with pytest.raises(TypeError):
#             storage_chest.set_request_filter("incorrect", "iron-ore", 100)
#         # with pytest.raises(InvalidItemError):
#         #     storage_chest.set_request_filter(1, "incorrect", 100)
#         with pytest.raises(TypeError):
#             storage_chest.set_request_filter(1, "iron-ore", "incorrect")
#         with pytest.raises(IndexError):
#             storage_chest.set_request_filter(-1, "iron-ore", 100)
#         with pytest.raises(IndexError):
#             storage_chest.set_request_filter(1000, "iron-ore", 100)
#         with pytest.raises(ValueError):
#             storage_chest.set_request_filter(1, "iron-ore", -1)

#     def test_set_request_filters(self):
#         storage_chest = LogisticStorageContainer()
#         # storage_chest.set_request_filters(
#         #     [("iron-ore", 200), ("copper-ore", 1000), ("small-lamp", 50)]
#         # )
#         storage_chest.request_filters = [("iron-ore", 200), ("copper-ore", 1000), ("small-lamp", 50)]
#         assert storage_chest.request_filters == RequestFilters(root=[
#             {"index": 1, "name": "iron-ore", "count": 200},
#             {"index": 2, "name": "copper-ore", "count": 1000},
#             {"index": 3, "name": "small-lamp", "count": 50},
#         ])
#         # storage_chest.set_request_filters([("iron-ore", 200)])
#         storage_chest.request_filters = [("iron-ore", 200)]
#         assert storage_chest.request_filters == RequestFilters(root=[
#             {"index": 1, "name": "iron-ore", "count": 200}
#         ])
#         # Errors
#         with pytest.raises(DataFormatError):
#             # storage_chest.set_request_filters([("iron-ore", 200), ("incorrect", 100)])
#             storage_chest.request_filters = [("iron-ore", 200), ("incorrect", 100)]
#         # Make sure that filters are unchanged if command fails
#         assert storage_chest.request_filters == RequestFilters(root=[
#             {"index": 1, "name": "iron-ore", "count": 200}
#         ])

#         with pytest.raises(DataFormatError):
#             # storage_chest.set_request_filters("very wrong")
#             storage_chest.request_filters = "very wrong"


# ################################################################################


# class TestRequestItemsMixin:
#     def test_set_item_request(self):
#         pass

#     def test_set_item_requests(self):
#         pass

#     # def test_remove_item_request(self):
#     #     pass


# ################################################################################


# class TestStackSizeMixin:
#     def test_set_stack_size_override(self):
#         inserter = Inserter()
#         inserter.override_stack_size = 1
#         assert inserter.override_stack_size == 1

#         with pytest.raises(DataFormatError):
#             inserter.override_stack_size = "100,000"

#     def test_set_circuit_stack_size_enabled(self):
#         inserter = Inserter()
#         inserter.circuit_stack_size_enabled = True
#         assert inserter.circuit_stack_size_enabled == True

#         inserter.circuit_stack_size_enabled = None
#         assert inserter.circuit_stack_size_enabled == None

#         with pytest.raises(DataFormatError):
#             inserter.circuit_stack_size_enabled = "incorrect"

#     def test_set_stack_control_signal(self):
#         inserter = Inserter()
#         inserter.stack_size_control_signal = "signal-A"
#         assert inserter.stack_size_control_signal == SignalID(**{"name": "signal-A", "type": "virtual"})

#         inserter.stack_size_control_signal = SignalID(**{"name": "signal-A", "type": "virtual"})

#         inserter.stack_size_control_signal = None
#         assert inserter.stack_size_control_signal == None

#         # Warnings
#         with pytest.warns(UnknownSignalWarning):
#             inserter.stack_size_control_signal = {"name": "unknown", "type": "item"}

#         # Errors
#         with pytest.raises(DataFormatError):
#             inserter.stack_size_control_signal = TypeError
#         with pytest.raises(DataFormatError):
#             inserter.stack_size_control_signal = "wrong_name_lol"
