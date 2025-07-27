const container = document.getElementById("pedido-finalizado");

      let produtosPedido = [];
      let total = localStorage.getItem("totalPedido") || "0.00";
      const urlParams = new URLSearchParams(window.location.search);
      const pedidoId = urlParams.get("pedidoId");

      try {
        const dados = localStorage.getItem("produtosPedido");
        if (dados) {
          produtosPedido = JSON.parse(dados);
        }
      } catch (e) {
        console.error("Erro ao ler produtos do localStorage:", e);
      }

      if (produtosPedido.length === 0) {
        container.innerHTML = "<p>Nenhum produto encontrado no pedido.</p>";
      } else {
        produtosPedido.forEach((p) => {
          const div = document.createElement("div");
          div.className = "produto";
          div.innerHTML = `<strong>${p.nome}</strong> - R$ ${p.preco.toFixed(
            2
          )}`;
          container.appendChild(div);
        });

        const totalDiv = document.createElement("div");
        totalDiv.innerHTML = `<h3>Total do Pedido: R$ ${parseFloat(
          total
        ).toFixed(2)}</h3>`;
        container.appendChild(totalDiv);

        const statusDiv = document.createElement("div");
        statusDiv.className = "status-pagamento";
        statusDiv.innerHTML = `<span>⏳</span> Status: Aguardando Pagamento`;
        container.appendChild(statusDiv);

        const botaoPagamento = document.createElement("button");
        botaoPagamento.textContent = "Ir para Pagamento";
        botaoPagamento.onclick = () => {
          const produtosURL = produtosPedido
            .map((p) => `produto=${encodeURIComponent(p.nome)}`)
            .join("&");

          localStorage.removeItem("produtosPedido");
          localStorage.removeItem("totalPedido");

          let url = `/pages/pagamento.html?${produtosURL}`;
          if (pedidoId) {
            url += `&pedidoId=${pedidoId}`;
          }

          window.location.href = url;
        };
        container.appendChild(botaoPagamento);
      }
      