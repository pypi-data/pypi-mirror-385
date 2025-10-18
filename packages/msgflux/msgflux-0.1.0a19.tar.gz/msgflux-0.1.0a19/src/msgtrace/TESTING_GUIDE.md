# msgtrace - Guia de Testes

Como testar todas as features implementadas em msgtrace.

---

## 🚀 Setup Inicial

### 1. Build do Frontend

```bash
cd /home/vilson-neto/Documents/msg-projects/msgflux/src/msgtrace/frontend
npm install
npm run build
cd ../../..
```

**Resultado Esperado**:
```
✓ 1552 modules transformed
✓ built in 3.71s
dist/index.html                   0.48 kB │ gzip:  0.30 kB
dist/assets/index-*.css           19.00 kB │ gzip:  4.21 kB
dist/assets/index-*.js           259.82 kB │ gzip: 76.59 kB
```

### 2. Start do Servidor

```bash
msgtrace start --port 4321
```

**Resultado Esperado**:
```
INFO: Started server process
INFO: Waiting for application startup.
INFO: OTLP collector started
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:4321
```

### 3. Abrir Browser

```bash
open http://localhost:4321
```

**Resultado Esperado**:
- Dashboard carrega
- WebSocket conecta (veja no console: "✅ WebSocket: Connected...")
- Loading skeletons aparecem brevemente

---

## ✅ Teste 1: Real-Time Updates & Toast Notifications

### Objetivo:
Verificar que traces aparecem automaticamente no dashboard sem refresh manual.

### Passos:

1. **Abra o Dashboard** no browser:
   ```
   http://localhost:4321/dashboard
   ```

2. **Em outro terminal**, execute:
   ```bash
   python -m msgtrace.examples.e2e_example
   ```

3. **Observe**:
   - ✅ Toast notifications aparecem no canto inferior direito
   - ✅ "New trace captured: abc123def456..."
   - ✅ Stats cards atualizam automaticamente
   - ✅ Recent traces section atualiza automaticamente
   - ✅ Console mostra: "📊 New trace: ..."

### Critérios de Sucesso:
- [ ] Toast aparece para cada trace
- [ ] Dashboard atualiza sem refresh
- [ ] WebSocket permanece conectado
- [ ] Stats refletem novos traces

---

## ✅ Teste 2: Loading Skeletons

### Objetivo:
Verificar que skeletons aparecem durante carregamento.

### Passos:

1. **Limpe o cache do browser** (Cmd/Ctrl + Shift + R)

2. **Recarregue a página**

3. **Observe**:
   - ✅ Skeletons animados aparecem primeiro
   - ✅ Stats cards mostram skeletons
   - ✅ Trace list mostra skeletons
   - ✅ Conteúdo real substitui skeletons

### Critérios de Sucesso:
- [ ] Skeletons aparecem imediatamente
- [ ] Animação de pulse é suave
- [ ] Transição para conteúdo real é limpa
- [ ] Sem "flash" de conteúdo

---

## ✅ Teste 3: Error Handling

### Objetivo:
Verificar que erros são tratados gracefully.

### Passos:

1. **Stop o backend**:
   ```bash
   # Ctrl+C no terminal do msgtrace
   ```

2. **No browser**, tente:
   - Navegar para Traces
   - Recarregar Dashboard

3. **Observe**:
   - ✅ Error state aparece
   - ✅ Mensagem clara: "Failed to Load Dashboard"
   - ✅ Botão "Try Again" aparece
   - ✅ WebSocket tenta reconnect (5 tentativas)

4. **Start o backend novamente**:
   ```bash
   msgtrace start --port 4321
   ```

5. **Clique "Try Again"**:
   - ✅ Dashboard carrega normalmente

### Critérios de Sucesso:
- [ ] Error state é claro e acionável
- [ ] "Try Again" funciona
- [ ] WebSocket reconnecta automaticamente
- [ ] Sem crashes ou telas brancas

---

## ✅ Teste 4: Tooltips

### Objetivo:
Verificar que tooltips fornecem contexto útil.

### Passos:

1. **No Dashboard**, passe o mouse sobre:
   - Card "Total Traces"
   - Card "Errors"
   - Card "Error Rate"
   - Card "Avg Duration"

2. **Observe**:
   - ✅ Tooltip aparece após ~300ms
   - ✅ Texto explicativo é mostrado
   - ✅ Posicionamento correto acima do card
   - ✅ Tooltip desaparece ao mover mouse

### Critérios de Sucesso:
- [ ] Tooltips aparecem consistentemente
- [ ] Delay é apropriado (não muito rápido/lento)
- [ ] Texto é útil e claro
- [ ] Estilo é consistente

---

## ✅ Teste 5: Trace Comparison

### Objetivo:
Comparar dois traces lado a lado.

### Passos:

1. **Gere alguns traces**:
   ```bash
   python -m msgtrace.examples.basic_tracing
   ```

2. **Vá para Traces**:
   ```
   http://localhost:4321/traces
   ```

3. **Copie 2 trace IDs**:
   - Clique em um trace para ver detalhes
   - Copie o trace_id da URL
   - Repita para outro trace

4. **Acesse Compare**:
   ```
   http://localhost:4321/traces/compare?trace1=XXX&trace2=YYY
   ```

5. **Observe**:
   - ✅ Dois cards lado a lado (azul vs verde)
   - ✅ Summary cards mostram diferenças
   - ✅ Duration diff com % e indicador (faster/slower)
   - ✅ Span breakdown table com comparações
   - ✅ Links "View Details" funcionam

### Critérios de Sucesso:
- [ ] Layout side-by-side funciona
- [ ] Diferenças são calculadas corretamente
- [ ] Cores indicam performance (verde=better, vermelho=worse)
- [ ] Span breakdown é útil

---

## ✅ Teste 6: Empty States

### Objetivo:
Verificar mensagens quando não há dados.

### Passos:

1. **Limpe o banco de dados**:
   ```bash
   msgtrace clear
   ```

2. **Recarregue o Dashboard**

3. **Observe**:
   - ✅ Stats mostram 0
   - ✅ "No traces found. Start tracing..." aparece
   - ✅ Ícone apropriado é mostrado
   - ✅ Mensagem é clara e acionável

### Critérios de Sucesso:
- [ ] Empty state é visível e claro
- [ ] Não há erros no console
- [ ] Mensagem guia o usuário
- [ ] Estilo é consistente

---

## ✅ Teste 7: Timeline Visualization

### Objetivo:
Visualizar spans ao longo do tempo.

### Passos:

1. **Gere traces complexos**:
   ```bash
   python -m msgtrace.examples.agent_tracing
   ```

2. **Abra um trace com muitos spans**

3. **Selecione "Timeline" view**

4. **Observe**:
   - ✅ Spans aparecem como barras horizontais
   - ✅ Posicionamento reflete tempo de início
   - ✅ Largura reflete duração
   - ✅ Cores indicam status (azul=success, vermelho=error)
   - ✅ Hover mostra detalhes
   - ✅ Click abre span details modal

### Critérios de Sucesso:
- [ ] Timeline é legível
- [ ] Overlaps são visíveis (spans paralelos)
- [ ] Cores são significativas
- [ ] Interação funciona

---

## ✅ Teste 8: Tree View

### Objetivo:
Visualizar hierarquia de spans.

### Passos:

1. **No mesmo trace**, selecione "Tree View"

2. **Observe**:
   - ✅ Spans organizados hierarquicamente
   - ✅ Indentação mostra parent-child
   - ✅ Expand/collapse funcionam
   - ✅ Ícones de status (✅/❌)
   - ✅ Duração e span kind visíveis

3. **Teste expand/collapse**:
   - Click em spans com children
   - Verifique que children aparecem/desaparecem

### Critérios de Sucesso:
- [ ] Hierarquia é clara
- [ ] Expand/collapse funciona smoothly
- [ ] Status icons são corretos
- [ ] Performance é boa (mesmo com muitos spans)

---

## ✅ Teste 9: Span Details Modal

### Objetivo:
Ver detalhes completos de um span.

### Passos:

1. **Click em qualquer span** (timeline ou tree)

2. **Observe o modal**:
   - ✅ Nome e ID do span
   - ✅ Duration e timestamps
   - ✅ Span kind
   - ✅ Status (OK/ERROR)
   - ✅ **LLM Information** (se aplicável):
     - Model name
     - Token usage (input/output/total)
     - Costs (input/output/total)
   - ✅ Attributes (JSON formatted)
   - ✅ Events (se houver)
   - ✅ Resource attributes

3. **Teste close**:
   - Click no X
   - Click fora do modal
   - ESC key

### Critérios de Sucesso:
- [ ] Modal abre rapidamente
- [ ] Todas informações são visíveis
- [ ] LLM metrics destacados
- [ ] Close funciona de múltiplas formas

---

## ✅ Teste 10: Search & Filtering

### Objetivo:
Filtrar traces eficientemente.

### Passos:

1. **Vá para Traces list**

2. **Teste Search**:
   - Digite parte de um trace ID
   - Digite nome de workflow
   - Digite nome de service

3. **Observe**:
   - ✅ Resultados filtram em real-time
   - ✅ Matching é case-insensitive
   - ✅ Sem resultados mostra empty state

4. **Teste Filters**:
   - Click "Filters" button
   - Configure:
     - Workflow name
     - Min duration
     - Has errors (Yes/No/All)
   - Apply filters

5. **Observe**:
   - ✅ Resultados refletem filtros
   - ✅ Multiple filtros funcionam juntos
   - ✅ Clear filters restaura tudo

### Critérios de Sucesso:
- [ ] Search é responsivo
- [ ] Filters funcionam corretamente
- [ ] UI reflete estado atual
- [ ] Performance é boa

---

## ✅ Teste 11: Pagination

### Objetivo:
Navegar grandes listas de traces.

### Passos:

1. **Gere muitos traces** (50+):
   ```bash
   # Run multiple times
   python -m msgtrace.examples.basic_tracing
   ```

2. **Na Trace list**:
   - Observe botões Previous/Next
   - Click "Next"
   - Observe contador "Showing X-Y of Z"

3. **Teste navegação**:
   - Vá para próxima página
   - Volte para anterior
   - Verifique que primeiro/último desabilitam apropriadamente

### Critérios de Sucesso:
- [ ] Pagination funciona
- [ ] Botões desabilitam corretamente
- [ ] Contador é preciso
- [ ] Performance é boa

---

## ✅ Teste 12: WebSocket Reconnect

### Objetivo:
Verificar resiliência da conexão WebSocket.

### Passos:

1. **Com Dashboard aberto**, stop o backend:
   ```bash
   # Ctrl+C
   ```

2. **Observe console**:
   - ✅ "WebSocket disconnected"
   - ✅ "Reconnecting in Xms (attempt Y)"

3. **Start backend novamente**:
   ```bash
   msgtrace start --port 4321
   ```

4. **Observe**:
   - ✅ "✅ WebSocket: Connected..."
   - ✅ Reconnect automático
   - ✅ Dashboard funciona normalmente

### Critérios de Sucesso:
- [ ] Reconnect tenta 5x com backoff
- [ ] Sucesso quando backend volta
- [ ] Sem erros persistentes
- [ ] Funcionalidade restaurada

---

## 🎯 Teste Completo End-to-End

### Objetivo:
Workflow completo de trace generation → visualization.

### Passos:

1. **Start fresh**:
   ```bash
   msgtrace clear
   msgtrace start --port 4321
   ```

2. **Abra Dashboard** (deixe aberto)

3. **Em outro terminal**:
   ```bash
   python -m msgtrace.examples.e2e_example
   ```

4. **Observe sequência**:
   - ✅ Traces são gerados
   - ✅ Toasts aparecem no Dashboard
   - ✅ Stats atualizam
   - ✅ Recent traces lista cresce
   - ✅ Click em trace abre detalhes
   - ✅ Timeline mostra spans
   - ✅ Tree view funciona
   - ✅ Span details abre ao click
   - ✅ LLM metrics são visíveis
   - ✅ Compare dois traces funciona

### Critérios de Sucesso:
- [ ] Fluxo completo sem erros
- [ ] Real-time updates funcionam
- [ ] Todas visualizações carregam
- [ ] Performance é aceitável

---

## 📊 Checklist Final

### Backend:
- [ ] Server inicia sem erros
- [ ] OTLP collector funciona
- [ ] SQLite storage persiste dados
- [ ] WebSocket endpoint responde
- [ ] REST API funciona
- [ ] Health check retorna 200

### Frontend:
- [ ] Build completa sem erros
- [ ] Todas páginas carregam
- [ ] WebSocket conecta
- [ ] Toasts aparecem
- [ ] Skeletons funcionam
- [ ] Error states funcionam
- [ ] Tooltips aparecem
- [ ] Comparação funciona

### Integration:
- [ ] Frontend comunica com backend
- [ ] WebSocket recebe eventos
- [ ] Traces são visualizados corretamente
- [ ] Real-time updates funcionam
- [ ] Métricas são precisas

---

## 🐛 Problemas Comuns

### Frontend não carrega:
```bash
# Rebuild frontend
cd src/msgtrace/frontend
npm run build
```

### WebSocket não conecta:
- Verifique CORS settings
- Check browser console
- Verify backend está rodando

### Toasts não aparecem:
- Check WebSocket connection
- Verify console logs
- Test with example script

### Performance lenta:
- Reduce polling interval
- Clear old traces
- Check database size

---

## ✅ Conclusão

Se todos os testes passarem, você tem um msgtrace completamente funcional com:

- ✅ Real-time updates
- ✅ Toast notifications
- ✅ Trace comparison
- ✅ Loading skeletons
- ✅ Error handling
- ✅ Tooltips
- ✅ All visualizations working

**Status**: 🎉 **Ready for Production!**

---

**Próximo Passo**: Use com seus workflows reais e colete feedback!
