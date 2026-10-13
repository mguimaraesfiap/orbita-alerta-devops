using MongoDB.Driver;
using OrbitaAlerta.Api.Models;

namespace OrbitaAlerta.Api.Repositories;

public sealed class MongoAlertRepository : IAlertRepository
{
    private readonly IMongoCollection<Alert> _collection;

    public MongoAlertRepository(IMongoClient client, IConfiguration configuration)
    {
        var databaseName = configuration["MONGO_DATABASE"] ?? "orbita_alerta_esg";
        _collection = client.GetDatabase(databaseName).GetCollection<Alert>("alerts");
    }

    public async Task<IReadOnlyList<Alert>> GetAllAsync(CancellationToken cancellationToken) =>
        await _collection.Find(FilterDefinition<Alert>.Empty)
            .SortByDescending(alert => alert.CreatedAt)
            .ToListAsync(cancellationToken);

    public Task CreateAsync(Alert alert, CancellationToken cancellationToken) =>
        _collection.InsertOneAsync(alert, cancellationToken: cancellationToken);
}

