$(document).ready(function () {
    get_posts()
})

function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
    window.location.href = "/"
}

function get_posts() {
    $('#items').empty()
    $.ajax({
        type: "GET",
        url: "/get_posts",
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let item_list = response["item_list"]
                for (let i = 0; i < item_list.length; i++) {
                    let item = item_list[i]
                    let item_name = item["item_name"]
                    let img_path = item["img_path"]
                    let content_txt = item["content_txt"]
                    let html_temp = `<div class="col" id=${item_name}>
                                                <div class="card">
                                                    <a href="/items/${item_name}">
                                                        <img src="./static/${img_path}" class="card-img-top" alt="...">
                                                    </a>
                                                    <div class="card-body">
                                                        <h5 class="card-title">${item_name}</h5>
                                                        <p class="card-text">${content_txt}</p>
                                                    </div>
                                                </div>
                                            </div>`
                    $('#items').append(html_temp)
                }

            }
        }
    })

}