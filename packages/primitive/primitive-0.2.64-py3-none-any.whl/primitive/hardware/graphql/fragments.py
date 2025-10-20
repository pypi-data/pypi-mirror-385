hardware_fragment = """
fragment HardwareFragment on Hardware {
  id
  pk
  name
  slug
  createdAt
  updatedAt
  isAvailable
  isOnline
  isQuarantined
  isHealthy
  isController
  systemInfo
  hostname
  sshUsername
  manufacturer {
    id
    pk
    name
    slug
  }
  organization {
    id
    pk
    name
    slug
  }
  activeReservation {
    id
    pk
    status
    reservationNumber
    reason
    hardware {
      id
    }
    createdBy {
      username
    }
  }
}
"""
