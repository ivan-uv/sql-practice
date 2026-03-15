# Chinook Schema — Digital Music Store

## Tables

| Table | Key Columns |
|-------|-------------|
| **Artist** | ArtistId, Name |
| **Album** | AlbumId, Title, ArtistId → Artist |
| **Track** | TrackId, Name, AlbumId → Album, MediaTypeId, GenreId → Genre, Milliseconds, UnitPrice |
| **Genre** | GenreId, Name |
| **MediaType** | MediaTypeId, Name |
| **Playlist** | PlaylistId, Name |
| **PlaylistTrack** | PlaylistId → Playlist, TrackId → Track |
| **Customer** | CustomerId, FirstName, LastName, Email, Country, SupportRepId → Employee |
| **Invoice** | InvoiceId, CustomerId → Customer, InvoiceDate, BillingCountry, Total |
| **InvoiceLine** | InvoiceLineId, InvoiceId → Invoice, TrackId → Track, UnitPrice, Quantity |
| **Employee** | EmployeeId, FirstName, LastName, Title, ReportsTo → Employee |

## Relationships

```
Artist ──< Album ──< Track >── Genre
                    Track >── MediaType
                    Track ──< PlaylistTrack >── Playlist
Customer ──< Invoice ──< InvoiceLine >── Track
Customer >── Employee (SupportRepId)
Employee >── Employee (ReportsTo — self-referencing hierarchy)
```

## Useful Notes

- **Duration**: Track.Milliseconds — divide by 60000 to get minutes
- **Date functions**: `strftime('%Y', InvoiceDate)`, `strftime('%m', InvoiceDate)`
- **String concat**: `FirstName || ' ' || LastName`
- **Typical JOIN path for revenue by artist**:
  `Artist → Album → Track → InvoiceLine → Invoice`
