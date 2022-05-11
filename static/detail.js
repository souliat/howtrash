$(document).ready(function () {
    show_exp()
})
function show_exp() {
    $.ajax({
        type: "GET",
        url: "/data",
        data: {},
        success: function (response) {
            let rows = response['data']
            for (let i = 0; i < rows.length; i++){
                let name = rows[i]['name']
                let exp = rows[i]['exp']
                let img = rows[i]['url']
                let temp_html = `<div id="name" class="product_name">
                                    ${name}
                                </div>`

                let temp2_html = `${exp}`
                if (i == 0) {
                    $('#name').append(temp_html);
                    $('#exp-list').append(temp2_html);
                    $("#img").attr("src", img);}
                }
        }
    });
}
function save_detail() {
    let cate_in = $('#cate_in').val()
    let name_in = $('#name_in').val()
    let img_in = $('#img_in').val()
    let exp_in = $('#exp_in').val()
    $.ajax({
        type: 'POST',
        url: "/detail_data_admin",
        data: {'cate_in_give': cate_in, 'name_in_give': name_in, 'img_in_give': img_in, 'exp_in_give': exp_in},
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    })
};
