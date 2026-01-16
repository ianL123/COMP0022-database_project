package uk.ac.ucl.comp0010.groupproject06.config;

import static org.springframework.security.config.Customizer.withDefaults;

import java.util.Arrays;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * Configures security settings for the application.
 */
@Configuration
public class SecurityConfig {

  /**
   * Configures the security filter chain.
   *
   * @param http the HTTP security
   * @return the security filter chain
   * @throws Exception if an error occurs
   */
  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.csrf((csrf) -> csrf.disable()).cors(withDefaults());

    return http.build();
  }

  /**
   * Configures the CORS configuration source.
   *
   * @return the CORS configuration source
   */
  @Bean
  public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOriginPatterns(Arrays.asList("*"));
    config.setAllowedHeaders(Arrays.asList("*"));
    config.setAllowedMethods(Arrays.asList("*"));
    config.setAllowCredentials(false);
    config.applyPermitDefaultValues();

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);

    return source;
  }
}