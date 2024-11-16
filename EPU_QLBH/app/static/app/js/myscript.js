$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 2,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 4,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 6,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})


$('.remove-cart').click(function() {
    var id = $(this).attr("pid").toString();  // Lấy id sản phẩm
    var eml = this;  // Lưu trữ đối tượng button Xóa

    $.ajax({
        type: "GET",  // Đảm bảo phương thức là GET (hoặc POST nếu cần thiết)
        url: "/removecart",  // URL đúng với view xử lý
        data: {
            prod_id: id,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Đảm bảo token CSRF được gửi đi
        },
        success: function(data) {
            if (data.success) {  // Kiểm tra nếu dữ liệu trả về có success
                // Cập nhật lại số tiền và tổng tiền
                var amountElem = document.getElementById("amount");
                var totalAmountElem = document.getElementById("totalamount");

                if (amountElem) {
                    amountElem.innerText = data.amount;  // Cập nhật lại số tiền
                }

                if (totalAmountElem) {
                    totalAmountElem.innerText = data.totalamount;  // Cập nhật tổng tiền
                }

                // Xóa phần tử sản phẩm ra khỏi giỏ hàng (cart-item)
                $(eml).closest('.cart-item').remove();

                // Kiểm tra nếu giỏ hàng đã trống và thông báo cho người dùng
                if ($('.cart-item').length === 0) {
                    alert("Giỏ hàng của bạn đã trống!");
                }
            } else {
                alert('Không thể xóa sản phẩm');
            }
        },
        error: function(xhr, status, error) {
            console.error('Có lỗi xảy ra: ' + error);  // Kiểm tra lỗi nếu có
            alert('Có lỗi khi xóa sản phẩm');
        }
    });
});



$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            //alert(data.message)
            window.location.href = `http://127.0.0.1:8000/product-detail/${id}`
        }
    })
})


$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://127.0.0.1:8000/product-detail/${id}`
        }
    })
})