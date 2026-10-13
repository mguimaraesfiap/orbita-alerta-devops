using OrbitaAlerta.Api.Domain;
using OrbitaAlerta.Api.Models;
using Xunit;

namespace OrbitaAlerta.Api.Tests;

public class AlertValidatorTests
{
    [Fact]
    public void Should_accept_a_valid_alert()
    {
        var request = new CreateAlertRequest(
            "Qualidade do ar", "air-quality", "medium", "Curitiba", "Partículas acima do limite.");

        var result = AlertValidator.Validate(request);

        Assert.Empty(result);
    }

    [Fact]
    public void Should_reject_an_unknown_severity()
    {
        var request = new CreateAlertRequest(
            "Alerta", "environment", "urgent", "Curitiba", "Descrição.");

        var result = AlertValidator.Validate(request);

        Assert.Contains(nameof(CreateAlertRequest.Severity), result.Keys);
    }

    [Fact]
    public void Should_reject_missing_required_fields()
    {
        var request = new CreateAlertRequest("", "", "low", "", "");

        var result = AlertValidator.Validate(request);

        Assert.Equal(4, result.Count);
    }
}

