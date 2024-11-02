package fr.parisnanterre.neptune.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import fr.parisnanterre.neptune.backend.model.Hello;

@RestController
public class HelloController {
    @GetMapping("/")
    public String getHello() {
        return Hello.sayHello();
    }
}
