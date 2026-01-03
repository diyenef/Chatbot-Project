const {useState, useEffect, useRef} = React;

function ChatApp(props) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [tokens, setTokens] = useState(window.__INITIAL_TOKENS__ || 0);
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef(null);

  useEffect(() => {
    // fetch recent messages from server
    (async () => {
      try {
        const res = await fetch('/api/messages/?limit=50');
        const data = await res.json();
        if (data.ok) setMessages(data.messages.map(m => ({role: m.role, content: m.content})));
      } catch (err) {
        console.error('Could not load history', err);
      }
    })();
  }, []);

  useEffect(() => {
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [messages]);

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim()) return;
    if (tokens <= 0) return alert('Out of tokens. Please buy more.');
    const userMsg = {role: 'user', content: input};
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({message: input}),
      });
      const data = await res.json();
      if (!data.ok) {
        alert(data.error || 'Error');
      } else {
        setMessages(prev => [...prev, {role: 'bot', content: data.reply}]);
        setTokens(data.tokens);
      }
    } catch (err) {
      console.error(err);
      alert('Network error');
    } finally {
      setLoading(false);
      setInput('');
    }
  }

  async function buyTokens() {
    const amount = parseInt(prompt('How many tokens to buy?', '10'), 10);
    if (!amount || amount <= 0) return;
    try {
      const res = await fetch('/api/tokens/add/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({amount}),
      });
      const data = await res.json();
      if (data.ok) setTokens(data.tokens);
      else alert(data.error || 'Could not add tokens');
    } catch (err) {
      console.error(err);
      alert('Network error');
    }
  }

  return (
    <div>
      <div className="chat-window" ref={messagesRef}>
        {messages.map((m, i) => (
          <div key={i} className={"chat-row " + (m.role==='user' ? 'user' : 'bot')}>
            <div className={"bubble " + (m.role==='user' ? 'user' : 'bot')}>{m.content}</div>
          </div>
        ))}
      </div>

      <div className="chat-input">
        <textarea value={input} onChange={e=>setInput(e.target.value)} placeholder={tokens>0? 'Send a message...':'Out of tokens — buy more to continue.'} disabled={tokens<=0||loading} />
        <div style={{display:'flex',flexDirection:'column',gap:8}}>
          <button onClick={sendMessage} disabled={tokens<=0||loading} className="button">{loading? 'Sending...':'Send'}</button>
          <button onClick={buyTokens} type="button" className="button ghost">Buy</button>
        </div>
      </div>
    </div>
  );
}

const container = document.getElementById('app');
window.__INITIAL_TOKENS__ = window.__INITIAL_TOKENS__ || 0;
ReactDOM.createRoot(container).render(React.createElement(ChatApp));
