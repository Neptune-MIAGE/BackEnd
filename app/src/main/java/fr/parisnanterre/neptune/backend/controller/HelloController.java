package fr.parisnanterre.neptune.backend.controller;

import org.springframework.web.bind.annotation.RestController;

import fr.parisnanterre.neptune.backend.model.Hello;

import org.springframework.web.bind.annotation.GetMapping;


@RestController
public class HelloController {
    
    @GetMapping("/")
    public String getHello() {
        return Hello.sayHello();
    }
    
}
