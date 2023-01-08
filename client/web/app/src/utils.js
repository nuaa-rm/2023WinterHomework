export function closeWindow() {
    window?.pywebview?.api?.closeWindow()
}

export function minimizeWindow() {
    window?.pywebview?.api?.minimizeWindow()
}

export function localCompute(e) {
    return window?.pywebview?.api?.localCompute(e)
}

export function stepCompute(e) {
    return window?.pywebview?.api?.stepCompute(e)
}
