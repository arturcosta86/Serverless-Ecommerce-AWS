const API_URL = "https://pev6keanr8.execute-api.us-east-1.amazonaws.com/dev";

const container = document.getElementById("pagamento-container");
const urlParams = new URLSearchParams(window.location.search);
const pedidoId = urlParams.get("pedidoId");

container.innerHTML = '<h2>Informações de Pagamento</h2>';

const form = document.createElement("form");
form.className = "formulario-pagamento";
form.innerHTML = `
  <div class="form-group">
    <label for="numero">Número do Cartão</label>
    <input type="text" id="numero" required placeholder="0000 0000 0000 0000" maxlength="19">
  </div>
  <div class="form-group">
    <label for="nome">Nome no Cartão</label>
    <input type="text" id="nome" required placeholder="Seu nome completo">
  </div>
  <div class="form-row">
    <div class="form-group">
      <label for="validade">Validade</label>
      <input type="text" id="validade" required placeholder="MM/AA" maxlength="5">
    </div>
    <div class="form-group">
      <label for="cvv">CVV</label>
      <input type="text" id="cvv" required placeholder="123" maxlength="3">
    </div>
  </div>
  <button type="submit" class="btn">Finalizar Pagamento</button>
`;

form.addEventListener("submit", async function (event) {
  event.preventDefault();
  if (!pedidoId) {
    alert("ID do pedido não encontrado na URL.");
    return;
  }
  try {
    const response = await fetch(`${API_URL}/pagamentos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pedidoId: pedidoId,
        status: "pago",
        numero: document.getElementById("numero").value
      })
    });
    if (!response.ok) throw new Error("Erro ao confirmar pagamento");

    // CÓDIGO ATUALIZADO: Remove o redirecionamento automático e adiciona um botão
    container.innerHTML = `
      <div class="sucesso">
        ✅ Pagamento realizado com sucesso!<br>
        Obrigado pela sua compra.<br><br>
        ID do Pedido: <code>${pedidoId}</code>
      </div>
      <a href="/pages/meus-pedidos.html" class="btn" style="display: block; text-align: center; margin-top: 1rem;">Ver Meus Pedidos</a>
    `;
    
  } catch (error) {
    alert("Falha ao confirmar pagamento. Tente novamente.");
    console.error("Erro:", error);
  }
});

container.appendChild(form);