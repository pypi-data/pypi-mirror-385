# Terminal Tutor Zsh Real-Time Integration
# ZLE-based keystroke monitoring for instant command predictions

# Global state variables
typeset -g TT_CURRENT_PREDICTION=""
typeset -g TT_PREDICTION_DISPLAYED=""
typeset -g TT_LAST_BUFFER=""
typeset -g TT_REALTIME_ENABLED="1"
typeset -g TT_PREDICTION_LINES=""

# Performance cache
typeset -gA TT_PREDICTION_CACHE

# Terminal escape sequences (only set if not already defined)
[[ -z "$TT_SAVE_CURSOR" ]] && readonly TT_SAVE_CURSOR=$'\e[s'
[[ -z "$TT_RESTORE_CURSOR" ]] && readonly TT_RESTORE_CURSOR=$'\e[u'
[[ -z "$TT_MOVE_DOWN" ]] && readonly TT_MOVE_DOWN=$'\e[B'
[[ -z "$TT_CLEAR_LINE" ]] && readonly TT_CLEAR_LINE=$'\e[2K'
[[ -z "$TT_GREY_TEXT" ]] && readonly TT_GREY_TEXT=$'\e[90m'
[[ -z "$TT_RESET_COLOR" ]] && readonly TT_RESET_COLOR=$'\e[0m'

# Core prediction widget - called on every keystroke
tt_predict_realtime() {
    # Skip if disabled (check for disable file)
    [[ -f "/tmp/tt_disabled" ]] && return

    local current_buffer="$BUFFER"

    # Skip if buffer unchanged
    [[ "$current_buffer" == "$TT_LAST_BUFFER" ]] && return
    TT_LAST_BUFFER="$current_buffer"

    # Skip empty or space-prefixed buffers
    [[ -z "$current_buffer" || "$current_buffer" =~ ^[[:space:]] ]] && {
        tt_clear_prediction
        return
    }

    # Check cache first
    if [[ -n "${TT_PREDICTION_CACHE[$current_buffer]}" ]]; then
        local cached_prediction="${TT_PREDICTION_CACHE[$current_buffer]}"
        if [[ "$cached_prediction" != "$TT_CURRENT_PREDICTION" ]]; then
            tt_display_prediction "$cached_prediction"
        fi
        return
    fi

    # Get prediction from Terminal Tutor
    local prediction=""
    if command -v terminal-tutor >/dev/null 2>&1; then
        prediction=$(terminal-tutor predict "$current_buffer" 2>/dev/null)
    fi

    # Cache result
    TT_PREDICTION_CACHE[$current_buffer]="$prediction"

    # Display if changed
    if [[ "$prediction" != "$TT_CURRENT_PREDICTION" ]]; then
        if [[ -n "$prediction" ]]; then
            tt_display_prediction "$prediction"
        else
            tt_clear_prediction
        fi
    fi
}

# Display prediction below current line
tt_display_prediction() {
    local prediction="$1"

    # Clear existing prediction
    tt_clear_prediction

    # Handle multi-line predictions
    if [[ "$prediction" == *$'\n'* ]]; then
        # Multi-line prediction - display each line
        local lines=("${(@f)prediction}")
        local line_count=${#lines}

        # Save cursor position
        print -n "${TT_SAVE_CURSOR}"

        # Display each line
        for i in {1..$line_count}; do
            print -n "${TT_MOVE_DOWN}\r${TT_GREY_TEXT}${lines[i]}${TT_RESET_COLOR}"
        done

        # Restore cursor
        print -n "${TT_RESTORE_CURSOR}"

        # Store number of lines for cleanup
        TT_PREDICTION_LINES=$line_count
    else
        # Single line prediction
        print -n "${TT_SAVE_CURSOR}${TT_MOVE_DOWN}\r${TT_GREY_TEXT}${prediction}${TT_RESET_COLOR}${TT_RESTORE_CURSOR}"
        TT_PREDICTION_LINES=1
    fi

    TT_CURRENT_PREDICTION="$prediction"
    TT_PREDICTION_DISPLAYED="1"
}

# Clear prediction display
tt_clear_prediction() {
    [[ "$TT_PREDICTION_DISPLAYED" != "1" ]] && return

    # Clear multiple lines if needed
    local lines_to_clear=${TT_PREDICTION_LINES:-1}

    print -n "${TT_SAVE_CURSOR}"
    for i in {1..$lines_to_clear}; do
        print -n "${TT_MOVE_DOWN}\r${TT_CLEAR_LINE}"
    done
    print -n "${TT_RESTORE_CURSOR}"

    TT_CURRENT_PREDICTION=""
    TT_PREDICTION_DISPLAYED=""
    TT_PREDICTION_LINES=""
}

# Clean up on command execution
tt_cleanup_on_accept() {
    tt_clear_prediction

    # Periodic cache cleanup
    if (( ${#TT_PREDICTION_CACHE} > 100 )); then
        TT_PREDICTION_CACHE=()
    fi

    zle accept-line
}

# Handle backspace with prediction update
tt_handle_backward_delete() {
    zle backward-delete-char
    tt_predict_realtime
}

# Handle Ctrl+C
tt_handle_cancel() {
    tt_clear_prediction
    TT_PREDICTION_CACHE=()
    zle send-break
}

# Self-insert with prediction
tt_self_insert_and_predict() {
    zle self-insert
    tt_predict_realtime
}

# Register ZLE widgets
zle -N tt_predict_realtime
zle -N tt_cleanup_on_accept
zle -N tt_handle_backward_delete
zle -N tt_handle_cancel
zle -N tt_self_insert_and_predict

# Bind to key events
bindkey '^M' tt_cleanup_on_accept      # Enter
bindkey '^?' tt_handle_backward_delete  # Backspace
bindkey '^C' tt_handle_cancel          # Ctrl+C

# Bind printable characters to prediction function (completely silent)
if zle -l tt_self_insert_and_predict >/dev/null 2>&1; then
    for char in {a..z} {A..Z} {0..9} ' ' '-' '_' '.' '/' '=' ':' '@' '+' ',' '!' '?' '*' '%' '$' '#' '&' '(' ')' '[' ']' '{' '}' '<' '>' '|' ';' '"' "'" '`' '~'; do
        bindkey "$char" tt_self_insert_and_predict >/dev/null 2>&1 || :
    done
fi

# Utility functions (terminal-tutor CLI only interface)
tt_clear_cache() {
    TT_PREDICTION_CACHE=()
    echo "${TT_GREY_TEXT}🧹 Prediction cache cleared${TT_RESET_COLOR}"
}

# Hook cleanup on prompt display
precmd() {
    tt_clear_prediction
    TT_LAST_BUFFER=""
}

# Cleanup on exit
zshexit() {
    tt_clear_prediction
}

# Initialize (silent load)