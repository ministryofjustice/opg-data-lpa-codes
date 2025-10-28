package codes

type Status string

const (
	StatusSuperseded = Status("Superseded")
	StatusGenerated  = Status("Generated")
	StatusRevoked    = Status("Revoked")
)
