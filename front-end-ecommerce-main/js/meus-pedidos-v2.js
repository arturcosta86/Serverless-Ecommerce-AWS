// 🔧 Substitua pela URL do seu endpoint do API Gateway
const API_URL = "https://pev6keanr8.execute-api.us-east-1.amazonaws.com/dev";

const container = document.getElementById("lista-pedidos");

// Mostra uma mensagem de carregamento inicial
container.innerHTML = '<p>Carregando seus pedidos...</p>';

fetch(`${API_URL}/pedidos`)
  .then((res) => {
    if (!res.ok) {
        // Se a resposta não for OK (ex: 502, 403), lança um erro para ser pego pelo .catch()
        throw new Error(`Erro de rede ou servidor: ${res.status}`);
    }
    return res.json();
  })
  .then((pedidos) => {
    // Limpa a mensagem de "carregando"
    container.innerHTML = '';

    if (!Array.isArray(pedidos) || pedidos.length === 0) {
      container.innerHTML = "<p>Nenhum pedido encontrado.</p>";
      return;
    }

    pedidos.forEach((pedido) => {
      const div = document.createElement("div");
      div.className = "card-pedido";

      const produtosHTML = pedido.produtos?.map((nome) => `<li>${nome}</li>`).join("") || "<li>Nenhum produto listado.</li>";
      const status = pedido.status || "Status desconhecido";

      let statusClass = '';
      if (status.toLowerCase().includes('pago')) {
        statusClass = 'pago';
      } else if (status.toLowerCase().includes('cancelado')) {
        statusClass = 'cancelado';
      }

      let motivoHTML = "";
      if (status.toLowerCase() === "cancelado" && pedido.motivo) {
        motivoHTML = `<p><strong>Motivo:</strong> ${pedido.motivo}</p>`;
        if (pedido.motivo.toLowerCase().includes("cartão") || pedido.motivo.toLowerCase().includes("fraude")) {
          motivoHTML += `<p style="color:red;"><strong>🚨 O FBI vai bater na sua porta em breve...</strong></p>`;
        }
      }

      div.innerHTML = `
        <h3>Pedido #${pedido.pedidoId}</h3>
        <p><strong>Status:</strong> <span class="status ${statusClass}">${status}</span></p>
        <p><strong>Total:</strong> R$ ${parseFloat(pedido.total).toFixed(2)}</p>
        <p><strong>Produtos:</strong></p>
        <ul>${produtosHTML}</ul>
        ${motivoHTML}
      `;
      container.appendChild(div);
    });
  })
  .catch((err) => {
    console.error("Erro ao buscar pedidos:", err);
    container.innerHTML = '<div class="erro-container">❌ Erro ao carregar pedidos. Verifique se a URL da API está correta e se a função Lambda está funcionando.</div>';
  });