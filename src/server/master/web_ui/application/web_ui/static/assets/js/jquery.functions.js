/*
 *	jQuery Innerfade
 *  This plugin is used on the homepage.
*/


/* Application Showcase */
jQuery.noConflict();	
	jQuery(document).ready(function(){  	
		/*jQuery('#slider').innerfade({
				animationtype: 'fade', 
				speed: '3000',
				timeout: 3000,
				type: 'sequence',
				containerheight: 'auto'
		});*/
});

/* Client Testimonials */
jQuery.noConflict();	
	jQuery(document).ready(function(){  	
		jQuery('#slider2').innerfade({
				animationtype: 'fade', 
				speed: '3000',
				timeout: 5000,
				type: 'sequence',
				containerheight: 'auto'
		});	
});

/* Screenshots */
jQuery.noConflict();	
	jQuery(document).ready(function(){ 
		jQuery('.boxgrid.captionfull').hover(function(){ //On hover...
			jQuery(".cover", this).fadeIn("fast");
		}, 
		function() { //On hover out...
			jQuery(".cover", this).fadeOut("fast");
		});

});

/* Table Style */
jQuery.noConflict();	
	jQuery(document).ready(function(){  	
		jQuery(".pricing-table tr:odd").addClass("alt");	
	});
	
/* Lightbox */
jQuery.noConflict();	
    jQuery(document).ready(function(){
        jQuery('.boxgrid a').lightBox();
    });
