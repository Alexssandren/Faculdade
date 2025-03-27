public class TesteAnimais {
    public static void main(String[] args) {
        // Testando a classe Animal
        Animal animalGenerico = new Animal("Genérico", "Desconhecida", "Desconhecida", 5);
        System.out.println(animalGenerico.alimentar());
        
        // Testando a classe Mamifero
        Mamifero leao = new Mamifero("Leão", "Panthera leo", "Felídeos", 8, "Curta");
        System.out.println(leao.alimentar());
        System.out.println("Pelagem: " + leao.getTipoPelagem());
        
        // Testando a classe Ave
        Ave papagaio = new Ave("Papagaio", "Amazona aestiva", "Psittacidae", 3, "Curvo");
        System.out.println(papagaio.alimentar());
        System.out.println(papagaio.voar());
        System.out.println("Tipo de bico: " + papagaio.getTipoDeBico());
    }
}