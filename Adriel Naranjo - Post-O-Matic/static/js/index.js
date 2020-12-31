// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        posts: [], // See initialization.
        user_email : user_email
    };

    app.index = (a) => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;
        for (let p of a) {
            p._idx = i++;
            // TODO: Only make the user's own posts editable.
            p.editable = true;
            p.edit = false;
            p.is_pending = false;
            p.error = false;
            p.original_content = p.content; // Content before an edit.
            p.server_content = p.content; // Content on the server.
        }
        return a;
    };

    app.reindex = () => {
        // Adds to the posts all the fields on which the UI relies.
        let i = 0;


        // [Post1, .. , PostN]
        //      0 .. N
        // how the posts are indexed on the screen opposed to the database

        for (let p of app.vue.posts) {
            p._idx = i++;
        }
    };

    app.do_edit = (post_idx) => {
        // Handler for button that starts the edit.
        // TODO: make sure that no OTHER post is being edited.
        // If so, do nothing.  Otherwise, proceed as below.
        let p = app.vue.posts[post_idx];

        if (p.email === user_email){
            p.edit = true;
            p.is_pending = false;
        }
  
    };

    app.do_cancel = (post_idx) => {
        // Handler for button that cancels the edit.
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // If the post has not been saved yet, we delete it.
            app.vue.posts.splice(post_idx, 1);
            app.reindex();
        } else {
            // We go back to before the edit.
            p.edit = false;
            p.is_pending = false;
            p.content = p.original_content;
        }
    }

    app.do_save = (post_idx) => {
        // Handler for "Save edit" button.
        let p = app.vue.posts[post_idx];
        if (p.content !== p.server_content) { 
            p.is_pending = true;


            //add post to server
            axios.post(posts_url, {

                content: p.content,
                id: p.id,
                is_reply: p.is_reply,

            }).then((result) => {

                console.log("Received:", result.data);
                // TODO: You are receiving the post id (in case it was inserted),
                // and the content.  You need to set both, and to say that
                // the editing has terminated.

                // takes index and splice 
                // hide and reindex
                is_reply = p.is_reply

                if (is_reply === null){
                    app.vue.posts.splice(post_idx, 1)
                    // app.reindex()
    
                    app.vue.posts.splice(post_idx, 0, {
                        id: result.data.id,
                        edit: false,
                        editable: true,
                        content: result.data.content,
                        server_content: result.data.content,
                        original_content: "",
                        author: author_name,
                        email: user_email,
                        is_reply: null,
                    })
                    
    
                    app.reindex()

                } else {



                    app.vue.posts.splice(post_idx, 1)

                    let q = {
                        id: result.data.id,
                        edit: false,
                        editable: true,
                        content: result.data.content,
                        server_content: result.data.content,
                        original_content: "",
                        author: author_name,
                        email: user_email,
                        is_reply: p.is_reply,
                    };

                    app.data.posts.splice(post_idx, 0, q)
                    app.reindex()



                }


            }).catch((error) => {
                console.log("Caught error");
                console.log(error)
                // We stay in edit mode.
            });
        } else {
            // No need to save.
            p.edit = false;
            p.original_content = p.content;
        }
    }

    app.add_post = () => {
        // TODO: this is the new post we are inserting.
        // You need to initialize it properly, completing below, and ...
        let q = {
            id: null,
            edit: true,
            editable: true,
            content: "",
            server_content: null,
            original_content: "",
            author: null,
            email: null,
            is_reply: null,
        };
        // TODO: DONE
        // ... you need to insert it at the top of the post list.
        console.log("Adding post!")
        app.data.posts.unshift(q)
        app.reindex()
    };




    app.reply = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id !== null) {
            // TODO: this is the new reply.  You need to initialize it properly...
            let q = {
                id: null,
                edit: true,
                editable: true,
                content: "",
                server_content: null, //**double check these values later**
                original_content: "",
                author: null,
                email: null,
                is_reply: p.id,
            };
            // TODO: and you need to insert it in the right place, and reindex
            // the posts.  Look at the code for app.add_post; it is similar.
            app.data.posts.splice(post_idx + 1, 0, q)
            app.reindex()

        }
    };




    app.do_delete = (post_idx) => {
        let p = app.vue.posts[post_idx];
        if (p.id === null) {
            // TODO:
            // If the post has never been added to the server, simply deletes it.
            app.do_cancel(post_idx)
        } else {
            // TODO: Deletes it on the server.
            axios.post(delete_url, {id : p.id}).then((response)=> {
                console.log(response)
                app.vue.posts.splice(post_idx,1)
                app.reindex()

            }).catch((error)=> {console.log(error)})
        }
    };





    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        do_edit: app.do_edit,
        do_cancel: app.do_cancel,
        do_save: app.do_save,
        add_post: app.add_post,
        reply: app.reply,
        do_delete: app.do_delete,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // You should load the posts from the server.
        // This is purely debugging code.
        // posts = [
        //     // This is a post.
        //     {
        //         id: 1,
        //         content: "I love apples",
        //         author: "Joe Smith",
        //         email: "joe@ucsc.edu",
        //         is_reply: null, // Main post.  Followed by its replies if any.
        //     },
        //     {
        //         id: 2,
        //         content: "I prefer bananas",
        //         author: "Elena Degiorgi",
        //         email: "elena@ucsc.edu",
        //         is_reply: 1, // This is a reply.
        //     },
        //     {
        //         id: 3,
        //         content: "I prefer bananas",
        //         author: "Elena Degiorgi",
        //         email: "elena@ucsc.edu",
        //         is_reply: 1, // This is a reply.
        //     },
        // ];
        // We set the posts. This is how it is done in reality.
        
        // Send a request to the server for the posts
        axios.get(posts_url).then((result) => {
             
            console.log("Received:", result.data)

            posts = result.data.posts
            posts = app.index(posts)
            app.vue.posts = posts


        }).catch(()=> {
            // p.is_pending = false
            console.log("**ERROR:")
            console.log(error)
        });

        // app.vue.posts = app.index(posts);
        // TODO: Load the posts from the server instead.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
