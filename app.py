from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گروه جنگی 🔥</title>
    <script src="https://unpkg.com/@supabase/supabase-js@2"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lz-string/1.4.4/lz-string.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, sans-serif; }
        body { background-color: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 10px; }
        .app-container { background: #1e293b; width: 100%; max-width: 480px; border-radius: 12px; border: 1px solid #334155; overflow: hidden; display: flex; flex-direction: column; height: 95vh; }
        .modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 1000; }
        .modal-box { background: #1e293b; padding: 25px; border-radius: 12px; width: 90%; max-width: 350px; text-align: center; border: 1px solid #475569; }
        .header { padding: 12px; background: #0f172a; border-bottom: 1px solid #334155; }
        .user-info { font-size: 12px; color: #38bdf8; margin-bottom: 8px; display: flex; justify-content: space-between; }
        .group-title { text-align: center; padding: 8px; background: #1e293b; border-radius: 8px; margin-bottom: 8px; border: 1px solid #facc15; }
        .group-title h2 { color: #facc15; font-size: 18px; }
        .group-title span { color: #94a3b8; font-size: 12px; }
        .messages-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #0b1120; }
        .msg { max-width: 80%; padding: 8px 12px; border-radius: 10px; font-size: 13px; line-height: 1.5; word-break: break-word; }
        .msg.sent { align-self: flex-end; background: #0284c7; color: #fff; border-bottom-left-radius: 0; }
        .msg.received { align-self: flex-start; background: #334155; color: #e2e8f0; border-bottom-right-radius: 0; }
        .msg-sender { font-size: 10px; color: #facc15; margin-bottom: 3px; font-weight: bold; }
        .msg-time { font-size: 9px; opacity: 0.7; margin-top: 4px; text-align: left; }
        .msg-system { align-self: center; background: #475569; color: #94a3b8; font-size: 11px; padding: 4px 12px; border-radius: 20px; max-width: 90%; text-align: center; }
        .input-box { padding: 12px; background: #0f172a; border-top: 1px solid #334155; display: flex; gap: 8px; }
        input { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #475569; background: #1e293b; color: #fff; font-size: 13px; outline: none; }
        button { padding: 8px 12px; border-radius: 8px; border: none; background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; font-size: 12px; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div id="loginModal" class="modal" style="display: none;">
        <div class="modal-box">
            <h3 style="margin-bottom: 12px; color: #facc15;">🔥 ورود به گروه جنگی</h3>
            <p style="font-size: 12px; color: #94a3b8; margin-bottom: 15px;">لطفاً نام خود را وارد کنید:</p>
            <input type="text" id="modalUsername" placeholder="اسم شما...">
            <button onclick="registerUser()" style="width: 100%; margin-top: 10px; background: #facc15; color: #0f172a;">ورود به گروه 🚀</button>
        </div>
    </div>
    <div class="app-container">
        <div class="header">
            <div class="user-info">
                <span>👤 کاربر: <b id="currentUserLabel">...</b></span>
                <span id="memberCount" style="color: #22c55e;">👥 0 نفر</span>
            </div>
            <div class="group-title">
                <h2>🔥 گروه جنگی</h2>
                <span>💬 پیام‌ها در این گروه ذخیره می‌شوند</span>
            </div>
        </div>
        <div class="messages-box" id="messagesBox">
            <div class="msg-system">🔥 به گروه جنگی خوش آمدید!</div>
        </div>
        <div class="input-box">
            <input type="text" id="msgInput" placeholder="پیام خود را بنویسید..." disabled>
            <button onclick="sendMessage()" id="sendBtn" disabled>ارسال 🚀</button>
        </div>
    </div>
    <script>
        const SUPABASE_URL = "https://jimvkiprcbpqruvhyfrm.supabase.co";
        const SUPABASE_KEY = "sb_publishable_00YkZ5PxbALEn4O09XKgSw_KFQiSWE0";
        const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        const GROUP_NAME = "گروه جنگی";
        let myUsername = localStorage.getItem('chat_username');
        let fetchInterval = null;

        window.onload = async () => {
            if (!myUsername) {
                document.getElementById('loginModal').style.display = 'flex';
            } else {
                document.getElementById('currentUserLabel').innerText = myUsername;
                document.getElementById('msgInput').disabled = false;
                document.getElementById('sendBtn').disabled = false;
                await loadMessages();
                await updateMemberCount();
                startAutoRefresh();
            }
        };

        async function registerUser() {
            const nameInput = document.getElementById('modalUsername').value.trim();
            if (!nameInput) return alert("لطفاً نام را وارد کنید!");
            try {
                const { error } = await supabaseClient.from('users').insert([{ username: nameInput }]);
                if (error) { alert('خطا: ' + error.message); return; }
                localStorage.setItem('chat_username', nameInput);
                myUsername = nameInput;
                document.getElementById('currentUserLabel').innerText = myUsername;
                document.getElementById('loginModal').style.display = 'none';
                document.getElementById('msgInput').disabled = false;
                document.getElementById('sendBtn').disabled = false;
                await sendWelcomeMessage();
                await loadMessages();
                await updateMemberCount();
                startAutoRefresh();
            } catch(e) { alert('خطا: ' + e.message); }
        }

        async function sendWelcomeMessage() {
            const welcomeText = '👋 ' + myUsername + ' به گروه پیوست!';
            const compressedText = LZString.compressToUTF16(welcomeText);
            await supabaseClient.from('messages').insert([{
                sender: 'system',
                receiver: 'GROUP:' + GROUP_NAME,
                content: compressedText
            }]);
        }

        async function sendMessage() {
            const input = document.getElementById('msgInput');
            const rawText = input.value.trim();
            if (!rawText) return;
            const compressedText = LZString.compressToUTF16(rawText);
            input.value = '';
            const { error } = await supabaseClient.from('messages').insert([{
                sender: myUsername,
                receiver: 'GROUP:' + GROUP_NAME,
                content: compressedText
            }]);
            if (error) alert('خطا در ارسال: ' + error.message);
            else await loadMessages();
        }

        async function loadMessages() {
            const { data, error } = await supabaseClient
                .from('messages')
                .select('*')
                .eq('receiver', 'GROUP:' + GROUP_NAME)
                .order('created_at', { ascending: true });
            if (error) return;
            const box = document.getElementById('messagesBox');
            box.innerHTML = '';
            if (!data || data.length === 0) {
                box.innerHTML = '<div class="msg-system">🔥 گروه جنگی - هنوز پیامی ارسال نشده است</div>';
                return;
            }
            data.forEach(msg => {
                let text = LZString.decompressFromUTF16(msg.content);
                if (!text) text = msg.content;
                const isMe = msg.sender === myUsername;
                const isSystem = msg.sender === 'system';
                if (isSystem) {
                    const div = document.createElement('div');
                    div.className = 'msg-system';
                    div.innerText = text;
                    box.appendChild(div);
                    return;
                }
                const div = document.createElement('div');
                div.className = 'msg ' + (isMe ? 'sent' : 'received');
                const time = new Date(msg.created_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
                let senderHtml = !isMe ? '<div class="msg-sender">' + msg.sender + '</div>' : '';
                div.innerHTML = senderHtml + '<div>' + text + '</div><div class="msg-time">' + time + '</div>';
                box.appendChild(div);
            });
            box.scrollTop = box.scrollHeight;
        }

        async function updateMemberCount() {
            const { data } = await supabaseClient
                .from('messages')
                .select('sender')
                .eq('receiver', 'GROUP:' + GROUP_NAME);
            const members = new Set();
            (data || []).forEach(msg => {
                if (msg.sender !== 'system') members.add(msg.sender);
            });
            document.getElementById('memberCount').innerText = '👥 ' + members.size + ' نفر';
        }

        function startAutoRefresh() {
            if (fetchInterval) clearInterval(fetchInterval);
            fetchInterval = setInterval(async () => {
                await loadMessages();
                await updateMemberCount();
            }, 3000);
        }

        document.getElementById('msgInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
