"""Electricity meter GraphQL operations."""

ELECTRICITY_METER_READINGS_QUERY = """
query ElectricityMeterReadings($accountNumber: String!, $meterId: ID!) {
  electricityMeterReadings(accountNumber: $accountNumber, meterId: $meterId, first: 100) {
    edges { node { value readAt registerObisCode registerType } }
  }
}
"""
