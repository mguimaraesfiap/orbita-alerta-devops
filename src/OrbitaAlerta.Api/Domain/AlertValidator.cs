using OrbitaAlerta.Api.Models;

namespace OrbitaAlerta.Api.Domain;

public static class AlertValidator
{
    private static readonly string[] AllowedSeverities = ["low", "medium", "high", "critical"];

    public static Dictionary<string, string[]> Validate(CreateAlertRequest request)
    {
        var errors = new Dictionary<string, string[]>();

        AddIfEmpty(errors, nameof(request.Title), request.Title, "O título é obrigatório.");
        AddIfEmpty(errors, nameof(request.Category), request.Category, "A categoria é obrigatória.");
        AddIfEmpty(errors, nameof(request.City), request.City, "A cidade é obrigatória.");
        AddIfEmpty(errors, nameof(request.Description), request.Description, "A descrição é obrigatória.");

        if (string.IsNullOrWhiteSpace(request.Severity) ||
            !AllowedSeverities.Contains(request.Severity.Trim().ToLowerInvariant()))
        {
            errors[nameof(request.Severity)] = ["A severidade deve ser low, medium, high ou critical."];
        }

        return errors;
    }

    private static void AddIfEmpty(
        IDictionary<string, string[]> errors,
        string field,
        string? value,
        string message)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            errors[field] = [message];
        }
    }
}

