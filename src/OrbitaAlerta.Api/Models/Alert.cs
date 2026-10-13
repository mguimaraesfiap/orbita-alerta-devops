using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace OrbitaAlerta.Api.Models;

public sealed class Alert
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string? Id { get; set; }

    public required string Title { get; set; }
    public required string Category { get; set; }
    public required string Severity { get; set; }
    public required string City { get; set; }
    public required string Description { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
}

public sealed record CreateAlertRequest(
    string Title,
    string Category,
    string Severity,
    string City,
    string Description);

