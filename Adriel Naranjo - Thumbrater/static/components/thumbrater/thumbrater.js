(function(){

    var thumbRater = {
        props: ['url', 'callback_url'],
        data: null,
        methods: {}
    };

    thumbRater.data = function() {
        var data = {
            rating: 1, 
            get_url: this.url,
            set_url: this.callback_url
        };
        thumbRater.methods.load.call(data)
        return data
    }; 

    thumbRater.methods.load = function () {

        let self = this; 
        axios.get(self.get_url).then(function(res) {
            self.rating = res.data.rating
            console.log(res)
        })
    };

    thumbRater.methods.set_rating = function(saveRating) {
        // console.log(saveRating)
        this.rating = saveRating
        axios.get(this.set_url,
            { params: {'rating' : saveRating} } ).then((response) => {
                console.log(response)
            }).catch((error)=>{
                console.log(error)
            })
            
            
    }

    utils.register_vue_component('thumbrater', 'components/thumbrater/thumbrater.html',
        function(template) {
            thumbRater.template = template.data
            return thumbRater
        }); 


})();
