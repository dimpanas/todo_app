import axios from "axios";
import { useState } from "react";

function Login() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');


        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await axios.post('http://127.0.0.1:8000/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });
            
            const {access_token, refresh_token} = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            const tokenPayload = JSON.parse(atob(access_token.split('.')[1]));

            const userRole = tokenPayload.role;
            localStorage.setItem('user_role', userRole);

            if (userRole === 'admin') {
                console.log('Ανακατεύθυνση στο /admin-dashboard...');
            } else {
                console.log('Ανακατεύθυνση στο /dashboard...');
            }

            setMessage(`✅ Login successful ${userRole}!`);

        }catch (error) {
            console.log("Full Backend Error Object:", error.response);
            if (error.response?.data){
                setMessage(`❌ Error: ${error.response.data.message || error.response.data.detail ||'Connection failed'}`);
            }else {
                setMessage('❌ Could not connect to server')
            }

        } finally {
            setLoading(false);
        }

    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-900">
            <div className="w-full max-w-md space-y-6 rounded-2xl bg-white p-8 shadow-xl dark:bg-slate-800">

                <div className="text-center">
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                    Welcome
                </h2>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    Login to TO-DO App
                </p>
                </div>

                {message && (
                <div className={`p-3 rounded-lg text-sm text-center font-medium ${
                    message.includes('✅') 
                    ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
                    : 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                }`}>
                    {message}
                </div>
                )}

                <form className="space-y-5" onSubmit={handleSubmit}>
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
                            Username
                        </label>
                        <input
                            type="text"
                            value = {username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="your username"
                            required
                            className="w-full rounded-xl border border-slate-200 bg-transparent px-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:text-white"
                            disabled={loading}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
                        Password
                        </label>
                        <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="w-full rounded-xl border border-slate-200 bg-transparent px-4 py-3 text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700 dark:text-white" 
                        placeholder="••••••••"
                        disabled={loading}
                        />
                    </div>
                    <button
                        type = "submit"
                        className="w-full cursor-pointer rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition-all hover:bg-blue-700 hover:shadow-blue-500/30 active:scale-[0.98]"
                    >
                        {loading ? 'Γίνεται σύνδεση...' : 'Είσοδος'}
                    </button>
                </form>
            </div>
        </div>
    )

};

export default Login;