export function closeWindow() {
    window?.pywebview?.api?.closeWindow()
}

export function minimizeWindow() {
    window?.pywebview?.api?.minimizeWindow()
}

export function localCompute(e) {
    alert('test')
    return window?.pywebview?.api?.localCompute2({})
}

export function stepCompute(e) {
    return window?.pywebview?.api?.stepCompute(e)
}

// function sleep(time) {
//     return new Promise((resolve, _) => {
//         setTimeout(()=>{
//             resolve()
//         }, time)
//     })
// }

export function login() {
    return window?.pywebview?.api?.login()
}

export function initClient() {
    return window?.pywebview?.api?.initClient()
}

export function getName() {
    return window?.pywebview?.api?.getName()
}
