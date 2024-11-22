package fr.parisnanterre.neptune.backend.controller;

import org.springframework.web.bind.annotation.RestController;

import fr.parisnanterre.neptune.backend.model.Hello;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;

import org.springframework.web.bind.annotation.GetMapping;


@RestController
@Tag(name = "Hello Controller")
public class HelloController {
    
    @GetMapping("/hello")
    @Operation(
            summary = "Returns a welcome message",
            description = "This endpoint returns a simple message saying 'Hello from API'"
    )
    public String getHello() {
        return Hello.sayHello();
    }
    
}
