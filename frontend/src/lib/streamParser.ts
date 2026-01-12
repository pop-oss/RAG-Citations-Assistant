export type StreamEvent =
    | { type: 'token'; data: { token: string } }
    | { type: 'citations'; data: { citations: any[] } }
    | { type: 'done'; data: {} }
    | { type: 'error'; data: { message: string, code?: string } };

export async function parseSSEStream(
    reader: ReadableStreamDefaultReader<Uint8Array>,
    onEvent: (event: StreamEvent) => void
) {
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep the incomplete part

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6);
                try {
                    const data = JSON.parse(jsonStr);
                    // Determine event type based on data content
                    // Contract: "SSE 事件协议：token/citations/done/error"
                    // We assume the data object has a 'type' field or we infer it?
                    // Prompt says: "每个 event 的 data JSON 结构示例"
                    // Usually SSE has `event: type` line too.
                    // If the stream sends `event: token\ndata: {...}`, we need to parse `event` line.
                    // The parser above only looks for `data:`.

                    // Let's improve parser to handle `event:` line if present, or infer from data structure.
                    // If the backend sends standard SSE:
                    // event: token
                    // data: {"token": "hello"}
                    //
                    // My simplified parser might miss the `event` line if I only split by `\n\n`.
                    // Standard SSE uses `\n\n` between messages. Inside a message, `\n` separates fields.

                    // Improved logic:
                    // 1. Split block by `\n` to find `event:` and `data:`.

                    const fields = line.split('\n'); // This variable name might be confusing with the outer loop, but `line` here is actually a block if I split by `\n\n`.
                    // Wait, `lines` are blocks separated by `\n\n`. So `line` is one message block.
                    // Inside `line`, we might have newlines if it's "event: token\ndata: ...".
                    // BUT, `buffer.split('\n\n')` means `line` contains the whole message block.

                    let eventType = 'message';
                    let eventData = null;

                    const blockLines = line.split('\n');
                    for (const blockLine of blockLines) {
                        if (blockLine.startsWith('event: ')) {
                            eventType = blockLine.slice(7).trim();
                        } else if (blockLine.startsWith('data: ')) {
                            try {
                                eventData = JSON.parse(blockLine.slice(6));
                            } catch (e) {
                                console.error('Failed to parse JSON data', blockLine);
                            }
                        }
                    }

                    if (eventData) {
                        // Map to our StreamEvent type
                        if (eventType === 'token') onEvent({ type: 'token', data: eventData });
                        else if (eventType === 'citations') onEvent({ type: 'citations', data: eventData });
                        else if (eventType === 'done') onEvent({ type: 'done', data: eventData });
                        else if (eventType === 'error') onEvent({ type: 'error', data: eventData });
                        else {
                            // Fallback or infer
                            if (eventData.token) onEvent({ type: 'token', data: eventData });
                            else if (eventData.citations) onEvent({ type: 'citations', data: eventData });
                        }
                    }

                } catch (e) {
                    console.error('Parse error', e);
                }
            }
        }
    }
}
