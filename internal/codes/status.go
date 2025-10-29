package codes

type status string

const (
	statusSuperseded = status("Superseded")
	statusGenerated  = status("Generated")
	statusRevoked    = status("Revoked")
)
