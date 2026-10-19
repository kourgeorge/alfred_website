<?php
defined('ABSPATH') || exit;
$id = get_queried_object_id();
$lang = get_post_meta($id, '_alfred_lang', true) ?: 'he';
$dir = in_array($lang, array('he', 'ar'), true) ? 'rtl' : 'ltr';
$description = get_post_meta($id, '_alfred_description', true);
?><!doctype html>
<html lang="<?php echo esc_attr($lang); ?>" dir="<?php echo esc_attr($dir); ?>">
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width,initial-scale=1">
<?php if ($description) : ?><meta name="description" content="<?php echo esc_attr($description); ?>"><?php endif; ?>
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php
wp_body_open();
alfred_partial(get_post_meta($id, '_alfred_header', true) ?: $lang . '/header');
if (have_posts()) {
    while (have_posts()) {
        the_post();
        if (get_post_meta(get_the_ID(), '_alfred_route', true) !== '') {
            echo alfred_urls(get_the_content()); // Preserve the imported HTML and embeds.
        } else {
            echo '<main class="wrap section">';
            the_title('<h1>', '</h1>');
            the_content();
            echo '</main>';
        }
    }
} else {
    echo '<main class="wrap section"><h1>404</h1><p>Page not found.</p></main>';
}
alfred_partial(get_post_meta($id, '_alfred_footer', true) ?: $lang . '/footer');
wp_footer();
?>
</body>
</html>
