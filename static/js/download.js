
// ------- Datepicker  js --------//  
// 日期
$(document).ready(function () {
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        todayHighlight: true,
        beforeShowDay: function (date) {
            var currentMonth = new Date().getMonth(); // 當前月份
            var dateMonth = date.getMonth(); // 這一天所屬月份

            if (dateMonth === currentMonth) {
                return {
                    classes: 'current-month', // 設置當月日期的類名
                };
            } else {
                return {
                    classes: 'other-month', // 設置其他月份的類名
                };
            }
        }
    });
});
// 處理點擊按鈕事件
document.addEventListener('DOMContentLoaded', function () {
    // 收藏
    document.querySelectorAll('.keep').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();  // 阻止表單的默認提交行為
            const bookUrl = this.getAttribute('data-bookurl');
            const bookName = this.getAttribute('data-bookname');
            const formData = new FormData();
            formData.append('book_url', bookUrl);
            formData.append('book_name', bookName);

            fetch(gotokeep, {  // 正確的端點為/keep/
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);  // 在控制台印出提示訊息
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
    // 下載
    document.querySelectorAll('.download_button').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();  // 阻止表單的默認提交行為
            const bookUrl = this.getAttribute('data-bookurl');
            const bookName = this.getAttribute('data-bookname');
            const formData = new FormData();
            formData.append('book_url', bookUrl);
            formData.append('book_name', bookName);

            fetch(downloadUrl, {  // 正確的端點為/download/
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => {
                    if (response.ok) {
                        return response.blob();  // 处理为 Blob
                    } else {
                        throw new Error('下载失败，状态码：' + response.status);
                    }
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);  // 创建 Blob URL
                    const a = document.createElement('a');          // 创建下载链接
                    a.href = url;
                    a.download = bookName + '.txt';                // 设置下载文件名
                    document.body.appendChild(a);
                    a.click();  // 自动触发下载
                    a.remove(); // 下载完成后移除链接
                })
                .catch(error => {
                    console.error('错误:', error);
                });
        });
    });
    // 移除
    document.querySelectorAll('.dkbutton').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();  // 阻止表單的默認提交行為
            const bookUrl = this.getAttribute('data-bookurl');
            const bookName = this.getAttribute('data-bookname');
            const formData = new FormData();
            formData.append('book_url', bookUrl);
            formData.append('book_name', bookName);

            fetch(dkep, {  // 正確的端點為/keep/
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);  // 在控制台印出提示訊息
                    window.location.reload(); // 重新加載頁面
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    });
});
// 移除收藏
// document.addEventListener('DOMContentLoaded', function () {

// });
// function submitForm(bookurl) {
//     const form = document.getElementById('form-' + bookurl);
//     const formData = new FormData(form);

//     fetch(notelist, {
//         method: 'POST',
//         body: formData,
//         headers: {
//             'X-CSRFToken': csrfToken,
//         },
//     })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok ' + response.statusText);
//             }
//             return response.json();
//         })
//         .then(data => {
//             if (data.status === 'success') {
//                 // 使用新窗口打開一個空白頁面
//                 const newWindow = window.open('', '_blank');
//                 // 構造完整的 HTML 頁面
//                 newWindow.document.write(`
//                     <!DOCTYPE html>
//                     <html lang="zh">
//                     <head>
//                         <meta charset="UTF-8">
//                         <title>${data.bookname}</title>
//                     </head>
//                     <body>
//                         ${data.html} <!-- 返回的 HTML 內容 -->
//                     </body>
//                     </html>
//                 `);
//                 newWindow.document.close(); // 關閉文檔以使其可見
//                 // 將返回的 HTML 填充到新窗口中
//                 // newWindow.document.write(data.html);
//                 // newWindow.document.close(); // 關閉文檔以使其可見


//                 // // 設定新窗口的 URL
//                 // newWindow.location.href = '/note/notelist/';
//             } else {
//                 console.error('Error:', data.message);
//             }
//         })
//         .catch((error) => {
//             console.error('Error:', error);
//         });
// }
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // 判斷 cookie 名稱是否匹配
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}