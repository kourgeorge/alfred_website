<?php
defined('ABSPATH') || exit;

function alfred_routes() {
    return get_option('alfred_kour_routes', array());
}

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
});

add_filter('pre_get_document_title', function ($title) {
    $id = get_queried_object_id();
    return get_post_meta($id, '_alfred_route', true) !== '' ? get_the_title($id) : $title;
});

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('alfred-kour', get_template_directory_uri() . '/assets/style.css', array(), '1.0.0');
});

// Keep the imported HTML intact in the classic editor, including embeds.
add_filter('use_block_editor_for_post', function ($enabled, $post) {
    return get_post_meta($post->ID, '_alfred_route', true) !== '' ? false : $enabled;
}, 10, 2);

add_action('init', function () {
    foreach (alfred_routes() as $route => $id) {
        if ($route !== '/') {
            add_rewrite_rule('^' . preg_quote(trim($route, '/'), '#') . (substr($route, -1) === '/' ? '/?$' : '$'), 'index.php?page_id=' . absint($id), 'top');
        }
    }
});

add_filter('page_link', function ($url, $id) {
    $route = get_post_meta($id, '_alfred_route', true);
    return $route !== '' ? home_url($route) : $url;
}, 10, 2);

add_filter('redirect_canonical', function ($url) {
    return get_post_meta(get_queried_object_id(), '_alfred_route', true) !== '' ? false : $url;
});

function alfred_urls($html) {
    // Resolve local assets and links against this WordPress installation.
    return preg_replace_callback('~\b(href|src|action)=([\'"])/(?!/)([^\'"]*)\2~i', function ($match) {
        $path = $match[3];
        if (strpos($path, 'images/') === 0 || $path === 'style.css') {
            $url = get_template_directory_uri() . '/assets/' . $path;
        } else {
            $url = home_url('/' . $path);
        }
        return $match[1] . '=' . $match[2] . esc_url($url) . $match[2];
    }, $html);
}

function alfred_partial($name) {
    if ($name === 'none') {
        return;
    }
    if (!preg_match('~\A(?:he|en|ar|ru|fr)/[a-z-]+\z~', $name)) {
        return;
    }
    $file = get_template_directory() . '/partials/' . $name . '.html';
    if (is_file($file)) {
        echo alfred_urls(file_get_contents($file)); // Trusted theme HTML.
    }
}

function alfred_import_pages() {
    if (!current_user_can('manage_options')) {
        return new WP_Error('forbidden', 'Administrator access is required.');
    }
    $pages = json_decode(file_get_contents(get_template_directory() . '/pages.json'), true);
    if (!is_array($pages)) {
        return new WP_Error('invalid_bundle', 'The page bundle could not be read.');
    }
    $routes = alfred_routes();
    $count = 0;
    foreach ($pages as $page) {
        $route = $page['permalink'];
        // Re-running the importer preserves changes made in WordPress.
        if (isset($routes[$route]) && get_post($routes[$route])) {
            continue;
        }
        $id = wp_insert_post(wp_slash(array(
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_title' => $page['title'],
            'post_name' => $route === '/' ? 'alfred-home' : sanitize_title(str_replace('/', '-', trim($route, '/'))),
            'post_content' => $page['content'],
        )), true);
        if (is_wp_error($id)) {
            return $id;
        }
        foreach (array('lang', 'description', 'header', 'footer') as $key) {
            $default = in_array($key, array('header', 'footer'), true) ? $page['lang'] . '/' . $key : '';
            update_post_meta($id, '_alfred_' . $key, $page[$key] ?? $default);
        }
        update_post_meta($id, '_alfred_route', $route);
        $routes[$route] = $id;
        update_option('alfred_kour_routes', $routes);
        $count++;
    }
    if (isset($routes['/'])) {
        // Save the old homepage settings once so rollback is straightforward.
        if (get_option('alfred_kour_previous_home', false) === false) {
            add_option('alfred_kour_previous_home', array(
                'show_on_front' => get_option('show_on_front'),
                'page_on_front' => get_option('page_on_front'),
            ));
        }
        update_option('show_on_front', 'page');
        update_option('page_on_front', $routes['/']);
    }
    // Register new rules before flushing. Never change the site's permalink setting.
    foreach ($routes as $route => $id) {
        if ($route !== '/') {
            add_rewrite_rule('^' . preg_quote(trim($route, '/'), '#') . (substr($route, -1) === '/' ? '/?$' : '$'), 'index.php?page_id=' . absint($id), 'top');
        }
    }
    flush_rewrite_rules();
    return $count;
}

add_action('admin_menu', function () {
    add_management_page('Alfred website migration', 'Alfred migration', 'manage_options', 'alfred-migration', function () {
        echo '<div class="wrap"><h1>Alfred website migration</h1>';
        if (isset($_POST['alfred_import'])) {
            check_admin_referer('alfred_import');
            $result = alfred_import_pages();
            echo '<div class="notice notice-' . (is_wp_error($result) ? 'error' : 'success') . '"><p>';
            echo esc_html(is_wp_error($result) ? $result->get_error_message() : "Imported $result pages. Existing imported pages were preserved.");
            echo '</p></div>';
        }
        echo '<p>Imports the bundled pages and sets the Hebrew homepage. Existing WordPress content is retained. Back up the database and files before importing.</p>';
        echo '<form method="post">';
        wp_nonce_field('alfred_import');
        submit_button('Import website pages', 'primary', 'alfred_import');
        echo '</form></div>';
    });
});
