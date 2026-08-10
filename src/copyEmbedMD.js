(async () => {
    const seen = new WeakSet();
    const candidates = [];

    function looksLikeMessage(obj) {
        return obj && typeof obj === "object" && (obj.components || obj.embeds) && obj.id && obj.author;
    }

    function scan(obj, depth = 0) {
        if (!obj || typeof obj !== "object" || depth > 12) return;
        if (seen.has(obj)) return;
        seen.add(obj);

        if (looksLikeMessage(obj)) candidates.push(obj);

        if (Array.isArray(obj)) {
            for (const item of obj) scan(item, depth + 1);
            return;
        }

        for (const key of Object.keys(obj)) {
            if (key === "ownerDocument" || key === "parentNode" || key === "children") continue;
            try { scan(obj[key], depth + 1); } catch { }
        }
    }

    for (const el of document.querySelectorAll("*")) {
        for (const key of Object.keys(el)) {
            if (key.startsWith("__reactFiber$") || key.startsWith("__reactProps$")) {
                try { scan(el[key]); } catch { }
            }
        }
    }

    if (!candidates.length) {
        console.log("%cNo ephemeral message found. Make sure it is visible on screen.", "color:red;font-weight:bold");
        return;
    }

    // Sort by editedTimestamp or timestamp to ensure we get the absolute newest version
    candidates.sort((a, b) => {
        const timeA = new Date(a.editedTimestamp || a.timestamp || 0).getTime();
        const timeB = new Date(b.editedTimestamp || b.timestamp || 0).getTime();
        return timeA - timeB;
    });

    // Get the most recent message (now guaranteed to be the latest edit)
    const msg = candidates[candidates.length - 1];
    let extractedText = "";

    // 1. Extract Embeds
    if (msg.embeds && msg.embeds.length > 0) {
        for (const embed of msg.embeds) {
            if (embed.title) extractedText += `## ${embed.title}\n`;
            if (embed.description) extractedText += `${embed.description}\n`;
            if (embed.fields) {
                for (const field of embed.fields) extractedText += `**${field.name}**: ${field.value}\n`;
            }
        }
    }

    // 2. Extract Components (Type 10 is standard Markdown text in Discord UI)
    function extractComponents(components) {
        for (const comp of components) {
            if (comp.type === 10 && comp.content) {
                extractedText += `${comp.content}\n\n`;
            }
            if (comp.components) {
                extractComponents(comp.components);
            }
        }
    }

    if (msg.components) extractComponents(msg.components);

    // Clean up the text
    extractedText = extractedText.trim();

    if (!extractedText) {
        console.log("%cMessage found, but no text could be extracted.", "color:orange");
        console.log(msg);
        return;
    }

    console.log("%cExtracted Guide Text:", "color:#00ff88;font-weight:bold");
    console.log(extractedText);

    copy(extractedText);
    console.log("%cClean text copied to clipboard!", "color:#00ff88;font-weight:bold;font-size:14px");

})();
