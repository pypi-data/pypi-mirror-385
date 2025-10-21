; prompt-automation WSL2 Launcher
; Global hotkey: Ctrl+Shift+J
; Launches prompt-automation from WSL2 Ubuntu distribution

#Requires AutoHotkey v2.0

; Ctrl+Shift+J hotkey
^+j::
{
    ; Launch WSL2 command in hidden window
    Run "wsl.exe -d Ubuntu -- bash -c 'cd ~/prompt-automation && prompt-automation'", , "Hide"
    return
}

; Optional: Ctrl+Shift+Alt+J to launch with visible terminal (for debugging)
^+!j::
{
    Run "wsl.exe -d Ubuntu -- bash -c 'cd ~/prompt-automation && prompt-automation'"
    return
}
