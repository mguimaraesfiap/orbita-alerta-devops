using OrbitaAlerta.Api.Models;

namespace OrbitaAlerta.Api.Repositories;

public interface IAlertRepository
{
    Task<IReadOnlyList<Alert>> GetAllAsync(CancellationToken cancellationToken);
    Task CreateAsync(Alert alert, CancellationToken cancellationToken);
}

