"""SmartFlex GraphQL operations."""

SMARTFLEX_QUERY = """
query SmartFlex($accountNumber: String!) {
  completedDispatches(accountNumber: $accountNumber) { deltaKwh start startDt end endDt }
  devices(accountNumber: $accountNumber) {
    id name deviceType provider
    status {
      currentState isSuspended
      ... on SmartFlexVehicleStatus { activePower { value } stateOfCharge { value } }
      ... on SmartFlexChargePointStatus { stateOfCharge { value } }
    }
    ... on SmartFlexVehicle { vehicleVariant { batterySize } }
    ... on SmartFlexVehicle { chargingSessions(first: 100) { edges { node { start end energyAdded { value } cost { amount } ... on SmartFlexChargingSession { type } } } } }
    ... on SmartFlexChargePoint { chargingSessions(first: 100) { edges { node { start end energyAdded { value } cost { amount } ... on SmartFlexChargingSession { type } } } } }
  }
}
"""

SMART_CONTROL_MUTATION = """
mutation UpdateDeviceSmartControl($deviceId: ID!, $action: SmartControlAction!) {
  updateDeviceSmartControl(input: {deviceId: $deviceId, action: $action}) { id }
}
"""

BOOST_CHARGE_MUTATION = """
mutation UpdateBoostCharge($input: UpdateBoostChargeInput!) {
  updateBoostCharge(input: $input) { id }
}
"""
