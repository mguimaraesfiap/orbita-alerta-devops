using MongoDB.Driver;
using OrbitaAlerta.Api.Domain;
using OrbitaAlerta.Api.Models;
using OrbitaAlerta.Api.Repositories;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<IMongoClient>(_ =>
    new MongoClient(builder.Configuration["MONGO_CONNECTION_STRING"]
        ?? "mongodb://admin:change-me@localhost:27017/?authSource=admin"));
builder.Services.AddSingleton<IAlertRepository, MongoAlertRepository>();

var app = builder.Build();

app.MapGet("/health", (IHostEnvironment environment) =>
    Results.Ok(new
    {
        status = "healthy",
        service = "orbita-alerta-api",
        environment = environment.EnvironmentName
    }));

app.MapGet("/api/alerts", async (IAlertRepository repository, CancellationToken cancellationToken) =>
    Results.Ok(await repository.GetAllAsync(cancellationToken)));

app.MapPost("/api/alerts", async (CreateAlertRequest request, IAlertRepository repository, CancellationToken cancellationToken) =>
{
    var validation = AlertValidator.Validate(request);
    if (validation.Count > 0)
    {
        return Results.ValidationProblem(validation);
    }

    var alert = new Alert
    {
        Title = request.Title.Trim(),
        Category = request.Category.Trim(),
        Severity = request.Severity.Trim().ToLowerInvariant(),
        City = request.City.Trim(),
        Description = request.Description.Trim(),
        CreatedAt = DateTimeOffset.UtcNow
    };

    await repository.CreateAsync(alert, cancellationToken);
    return Results.Created($"/api/alerts/{alert.Id}", alert);
});

app.Run();

public partial class Program { }

