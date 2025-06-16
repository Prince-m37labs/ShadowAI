'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { HTMLAttributes } from 'react';

interface CodeComponentProps extends HTMLAttributes<HTMLElement> {
	inline?: boolean;
}

const MODES = [
	{ label: 'Readability', value: 'readability' },
	{ label: 'Performance', value: 'performance' },
	{ label: 'Modern ES6+ style', value: 'modern' },
];

export default function RefactorPage() {
	const [text, setText] = useState('');
	const [output, setOutput] = useState('');
	const [mode, setMode] = useState(MODES[0].value);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');
	const [copied, setCopied] = useState(false);

	const handleSubmit = async () => {
		if (!text.trim()) return;
		
		setLoading(true);
		setError('');
		setOutput('');
		setCopied(false);
		
		try {
			const res = await fetch('http://localhost:8000/refactor', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ code: text.trim(), mode }),
			});
			
			const data = await res.json();
			
			if (!res.ok) {
				throw new Error(data.detail || data.error || 'Failed to get response');
			}
			
			if (data.error) {
				throw new Error(data.error);
			}
			
			if (!data.refactored) {
				throw new Error('No refactored code received');
			}
			
			setOutput(data.refactored);
		} catch (e) {
			const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred';
			setError(errorMessage);
			console.error('Refactor Error:', e);
		} finally {
			setLoading(false);
		}
	};

	const handleCopy = () => {
		if (output) {
			navigator.clipboard.writeText(output);
			setCopied(true);
			setTimeout(() => setCopied(false), 1200);
		}
	};

	const handleReset = () => {
		setText('');
		setOutput('');
		setError('');
		setCopied(false);
	};

	return (
		<div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex items-center justify-center py-12">
			<div className="max-w-7xl w-full p-8 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-2xl shadow-2xl border border-[#232946] animate-fade-in">
				<h1 className="text-3xl font-extrabold mb-6 text-[#f6f7fb] tracking-tight flex items-center gap-2">
					<span className="animate">🛠️</span> Refactor Code
				</h1>
				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					{/* Input Section */}
					<div className="flex flex-col h-[500px]">
						<div className="mb-4">
							<label className="block font-semibold mb-2 text-[#a7adc6]">
								Refactor Mode
							</label>
							<select
								className="w-full border border-[#393e6e] rounded-lg p-2 bg-[#232946] text-[#f6f7fb] focus:outline-none focus:ring-2 focus:ring-[#f4acb7] transition"
								value={mode}
								onChange={(e) => setMode(e.target.value)}
							>
								{MODES.map((m) => (
									<option
										key={m.value}
										value={m.value}
										className="bg-[#232946] text-[#f6f7fb]"
									>
										{m.label}
									</option>
								))}
							</select>
						</div>
						<div className="flex-1 relative">
							<textarea
								className="w-full h-full border border-[#393e6e] rounded-lg p-3 bg-[#232946] text-[#f6f7fb] font-mono text-base transition focus:outline-none focus:ring-2 focus:ring-[#f4acb7] placeholder:text-[#f4acb7]/60 resize-none"
								placeholder="Paste your code here... 💡"
								value={text}
								onChange={(e) => setText(e.target.value)}
							/>
							<div className="absolute bottom-4 right-4 flex gap-3">
								<button
									className="px-5 py-2 bg-gradient-to-r from-[#f4acb7] to-[#a7c7e7] text-[#232946] font-bold rounded-lg shadow-lg hover:from-[#a7c7e7] hover:to-[#f4acb7] transition disabled:opacity-60 flex items-center gap-2"
									onClick={handleSubmit}
									disabled={loading || !text.trim()}
								>
									{loading ? (
										<span className="flex items-center gap-2 animate-pulse">
											<svg
												className="animate-spin h-4 w-4"
												viewBox="0 0 24 24"
											>
												<circle
													className="opacity-25"
													cx="12"
													cy="12"
													r="10"
													stroke="#f4acb7"
													strokeWidth="4"
													fill="none"
												/>
												<path
													className="opacity-75"
													fill="#f4acb7"
													d="M4 12a8 8 0 018-8v8z"
												/>
											</svg>
											Refactoring…
										</span>
									) : (
										<>
											<span className="animate-wiggle">🚀</span> Refactor
										</>
									)}
								</button>
								<button
									className="px-5 py-2 bg-[#232946] text-[#a7adc6] font-semibold rounded-lg border border-[#393e6e] hover:bg-[#393e6e] transition"
									onClick={handleReset}
									disabled={loading && !text && !output}
								>
									<span className="mr-1">♻️</span>Reset
								</button>
							</div>
						</div>
						{error && (
							<div className="mt-4 text-[#ffb4b4] bg-[#393e6e] border border-[#ffb4b4]/30 rounded-lg p-3 font-medium flex items-center gap-2 animate-shake">
								<span>❌</span> {error}
							</div>
						)}
					</div>

					{/* Output Section */}
					<div className="h-[500px]">
						{output ? (
							<div className="h-full bg-gradient-to-br from-[#393e6e] to-[#232946] rounded-xl border border-[#393e6e] shadow-lg animate-fade-in flex flex-col">
								<div className="p-4 border-b border-[#393e6e] bg-[#232946] rounded-t-xl">
									<h2 className="font-semibold text-[#a7adc6] flex items-center gap-2">
										<span className="animate-bounce">🧠</span> Refactored Code
									</h2>
								</div>
								<div className="flex-1 overflow-auto p-4">
									<button
										className={`absolute top-4 right-4 px-3 py-1 text-xs font-semibold rounded transition flex items-center gap-1 ${
											copied
												? 'bg-[#a7e7c7] text-[#232946]'
												: 'bg-[#f4acb7] text-[#232946] hover:bg-[#a7c7e7]'
										}`}
										onClick={handleCopy}
										title="Copy to clipboard"
									>
										{copied ? (
											<>
												<span className="animate-pulse">✅</span> Copied
											</>
										) : (
											<>
												<span>📋</span> Copy
											</>
										)}
									</button>
									<div className="prose prose-invert max-w-none">
										<ReactMarkdown
											components={{
												code: ({ inline, className, children, ...props }: CodeComponentProps) => {
													const match = /language-(\w+)/.exec(className || '');
													return !inline && match ? (
														<SyntaxHighlighter
															style={vscDarkPlus as any}
															language={match[1]}
															PreTag="div"
															{...props}
														>
															{String(children).replace(/\n$/, '')}
														</SyntaxHighlighter>
													) : (
														<code className={className} {...props}>
															{children}
														</code>
													);
												}
											}}
										>
											{output}
										</ReactMarkdown>
									</div>
								</div>
							</div>
						) : (
							<div className="h-full bg-gradient-to-br from-[#393e6e] to-[#232946] rounded-xl border border-[#393e6e] shadow-lg flex items-center justify-center">
								<div className="text-[#a7adc6] text-center">
									<div className="text-4xl mb-2">👨‍💻</div>
									<p className="text-lg">Your refactored code will appear here</p>
								</div>
							</div>
						)}
					</div>
				</div>
				<style jsx global>{`
					@keyframes fade-in {
						0% {
							opacity: 0;
							transform: translateY(16px);
						}
						100% {
							opacity: 1;
							transform: none;
						}
					}
					.animate-fade-in {
						animation: fade-in 0.7s cubic-bezier(0.4, 0, 0.2, 1) both;
					}
					@keyframes wiggle {
						0%,
						100% {
							transform: rotate(-3deg);
						}
						50% {
							transform: rotate(3deg);
						}
					}
					.animate-wiggle {
						animation: wiggle 0.7s infinite;
						display: inline-block;
					}
					@keyframes shake {
						0%,
						100% {
							transform: translateX(0);
						}
						20%,
						60% {
							transform: translateX(-6px);
						}
						40%,
						80% {
							transform: translateX(6px);
						}
					}
					.animate-shake {
						animation: shake 0.5s;
					}
				`}</style>
			</div>
		</div>
	);
}
