export type SseMessage = {
    event?: string;
    data: unknown;
};

export function parseSseMessages(buffer: string): {messages: SseMessage[]; rest: string} {
    const normalized = buffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const chunks = normalized.split('\n\n');
    const rest = chunks.pop() ?? '';

    return {
        messages: chunks.map(parseSseMessage).filter((message): message is SseMessage => Boolean(message)),
        rest,
    };
}

function parseSseMessage(raw: string): SseMessage | null {
    const lines = raw.split('\n');
    let event: string | undefined;
    const dataLines: string[] = [];

    lines.forEach((line) => {
        if (line.startsWith('event:')) {
            event = line.slice('event:'.length).trim();
        }
        if (line.startsWith('data:')) {
            dataLines.push(line.slice('data:'.length).trimStart());
        }
    });

    if (!dataLines.length) {
        return null;
    }

    const dataText = dataLines.join('\n');
    try {
        return {event, data: JSON.parse(dataText) as unknown};
    } catch {
        return {event, data: dataText};
    }
}
