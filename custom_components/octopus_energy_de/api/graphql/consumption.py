"""Electricity consumption GraphQL operations."""

ELECTRICITY_CONSUMPTION_QUERY = """
query ElectricityConsumption($accountNumber: String!, $propertyId: ID!, $date: Date!) {
  account(accountNumber: $accountNumber) {
    property(id: $propertyId) {
      measurements(
        utilityFilters: { electricityFilters: { readingFrequencyType: RAW_INTERVAL readingQuality: COMBINED } }
        startOn: $date
        first: 200
      ) {
        edges { node { ... on IntervalMeasurementType { startAt endAt unit value } } }
      }
    }
  }
}
"""
