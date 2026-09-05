from src.manager.token.token_budget_manager import NovaTokenBudgetManager
from src.manager.context.context_manager import NovaContextManager


# ============================================================
# MANAGERS
# ============================================================

context_manager = NovaContextManager()

token_manager = NovaTokenBudgetManager()


# ============================================================
# TOKEN SETTINGS
# ============================================================

chars_per_token = 4

provider = "lumialit"


# ============================================================
# CREATE CONTEXT
# ============================================================

context_filed = context_manager.create_provider_context(
    "Hii",
    "NEX-gnU1rvhcAAghQi8ukY9eYP3-OS",
    "NEX-o9UwzoNL5ZAadvU3Ixajzxl-OX"
)

context_Not_filed = context_manager.create_provider_context(
    "Hii",
    "NEX-E64LXl8jE04W6IvfZwdn1te-OS",
    "NEX-E64LXl8jE04W6IvfZwdn1te-OS"
)

context = context_filed


# ============================================================
# BEFORE TRIMMING
# ============================================================

print("\n========== BEFORE TRIMMING ==========\n")


memories_tokens = token_manager._estimate_tokens(
    context.memories,
    chars_per_token
)


conversation_tokens = token_manager._estimate_tokens(
    context.conversation,
    chars_per_token
)


message_tokens = token_manager._estimate_tokens(
    context.message,
    chars_per_token
)


total_tokens = (
    memories_tokens
    + conversation_tokens
    + message_tokens
)


print("Memories tokens =", memories_tokens)

print("Conversation tokens =", conversation_tokens)

print("Message tokens =", message_tokens)

print("Total tokens =", total_tokens)

print(
    "Fits budget =",
    token_manager.check_tokens(
        provider,
        context,
        chars_per_token
    )
)


# ============================================================
# TRIM CONVERSATION
# ============================================================

print("\n========== TRIMMING ==========\n")


trimmed_conversation = token_manager.trim_context(
    conversation=context.conversation,
    memories=context.memories,
    provider=provider,
    current_message=context.message,
    chars_per_token=chars_per_token
)


# ============================================================
# CREATE TRIMMED CONTEXT
# ============================================================

trimmed_context = {
    "messages": trimmed_conversation
}


# ============================================================
# AFTER TRIMMING
# ============================================================

print("\n========== AFTER TRIMMING ==========\n")


trimmed_conversation_tokens = token_manager._estimate_tokens(
    trimmed_context,
    chars_per_token
)


memories_tokens = token_manager._estimate_tokens(
    context.memories,
    chars_per_token
)


message_tokens = token_manager._estimate_tokens(
    context.message,
    chars_per_token
)


trimmed_total_tokens = (
    trimmed_conversation_tokens
    + memories_tokens
    + message_tokens
)


provider_budget = (
    token_manager.PROVIDER_LIMITS[provider]["budget"]
)


print("Memories tokens =", memories_tokens)

print(
    "Trimmed conversation tokens =",
    trimmed_conversation_tokens
)

print("Message tokens =", message_tokens)

print("Total tokens =", trimmed_total_tokens)

print("Provider budget =", provider_budget)

print(
    "Fits budget =",
    trimmed_total_tokens <= provider_budget
)


# ============================================================
# RESULT
# ============================================================

print("\n========== RESULT ==========\n")


print(
    "Messages remaining =",
    len(trimmed_conversation)
)


print(
    "Turns remaining ≈",
    len(trimmed_conversation) // 2
)


print(
    "Trimmed conversation =",
    trimmed_conversation
)
