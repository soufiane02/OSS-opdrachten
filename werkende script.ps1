Connect-AzureAD
$voornaam = "Soufiane"  # Vervang dit met jouw eigen voornaam

 

# Filteren op basis van de voornaam
$studentenMetZelfdeVoornaam = Get-AzureADUser -Filter "givenName eq '$voornaam'"

 

# Het aantal studenten met dezelfde voornaam tonen
$aantalStudenten = $studentenMetZelfdeVoornaam.Count
Write-Host "Aantal studenten met dezelfde voornaam: $aantalStudenten"
