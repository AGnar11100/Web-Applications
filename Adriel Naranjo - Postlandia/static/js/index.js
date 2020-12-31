// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        user_email: user_email,
        posts: [],
        showNewPost : false,
        newPostText : "", 
        text : "",
        userName : username
        // Complete.
    };

    // Add here the various functions you need.


    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {
        let idx = 0;
        for (p of a) {
            p._idx = idx++;
            p.showLikes = false
            p.known_likers = false
            p.like = ''
            p.dislike = ''
            // Add here whatever other attributes should be part of a post.
        }
        return a;
    };


    app.defaultLayout = function() {
        //when method is applied to plus button, v-on:click renders default layout which
        //allows for a post to be added
        app.data.showNewPost = !app.data.showNewPost

    }

    app.cancelMethod = function() {
        app.data.showNewPost = false
    }
 
    app.createPostMethod = function() {
        let text = app.data.text

        app.data.showNewPost = false
        
        data = {
            postText : text
        }

        axios.post(add_post_url, data).then(
            (response) => {
                let id = response.data.id
                
                new_post = {
                    name: app.data.userName,
                    post_text: app.data.text,
                    user_email : app.data.user_email,
                    id: id,
                    rating: {
                        rating: -1
                    }
                }

                app.data.posts.splice(0,0, new_post)
                app.data.posts = app.reindex(app.data.posts);
            })
    }

    app.deletePostMethod = function(postID, p_index) {
        id = event.target.id
        //delete_post comes from index.html XML transported URL
        axios.post(delete_post, {postID : postID}).then(
            (response) => {
                app.data.posts.splice(p_index,1)
                app.data.posts = app.reindex(app.data.posts);

            }).catch((error)=>{

            })
    }


    app.hoverOverThumbMethod = function(post_index){
        app.data.posts[post_index].showLikes = true

        let known = app.data.posts[post_index].known_likers

        if(!known){
        
        app.data.posts[post_index].like = ''
        app.data.posts[post_index].dislike = ''

        axios.post(likers_url, {post_id: post_id}).then((response) =>{

            let like = response.data.like
            let dislike = response.data.dislike

            app.data.posts[post_index].like = like 
            app.data.posts[post_index].dislike = dislike
            app.data.posts[post_index].known_likers = true 


        }).catch((error)=>{
            console.log(error)
        })

        }
    }

    app.hoverOffThumbMethod = function(post_index){
        app.data.posts[post_index].showLikes = false

    }

    app.addRatingMethod = function(post_id, ratingValue, post_index) {
        data = {
            id : post_id,
            rating: ratingValue
        }

        axios.post(thumbs_url, data).then((response)=>{
            console.log(response)
        }).catch((error)=>{
            
        })

        app.data.posts[post_index].rating.rating = ratingValue
        app.data.posts[post_index].known_likers = false

    }
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        renderDefault : app.defaultLayout,
        cancelButton : app.cancelMethod,
        createPost : app.createPostMethod,
        deletePost : app.deletePostMethod,
        hoverOverThumb : app.hoverOffThumbMethod,
        hoverOffThumb : app.hoverOffThumbMethod,
        addRating : app.addRatingMethod
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(get_posts_url).then((result) => {
            var post_list = result.data.posts
            var reversed_post_list = post_list.reverse()
            app.vue.posts = app.reindex(reversed_post_list);
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
