# 🔍 Code Smells - Guia de Detecção para Revisão

**IMPORTANTE:** Identifique problemas listados abaixo no código. Cada smell tem: sintoma, causa e solução.

## 🏗️ ARQUITETURA & DESIGN

### Large Class (God Class)
- **Sintoma:** Classe com muitas responsabilidades, métodos e atributos
- **Problema:** Violação SRP, difícil teste e manutenção
- **Exemplo:** `class User { login(), logout(), sendEmail(), calculateTax(), generateReport(), updateDatabase()... }`
- **Solução:** Extract Class, Extract Subclass

ref: https://luzkan.github.io/smells/large-class

### Long Method (God Method)
- **Sintoma:** Método com mais de 20-30 linhas ou múltiplas responsabilidades
- **Problema:** Difícil compreensão e teste
- **Exemplo:**
```js
function processOrder() {
  // valida dados - 15 linhas
  // calcula desconto - 20 linhas
  // atualiza estoque - 10 linhas
  // envia email - 15 linhas
  // gera relatório - 20 linhas
}
```
- **Solução:** Extract Method, Replace with Command

ref: https://luzkan.github.io/smells/long-method

### Long Parameter List
- **Sintoma:** 3+ parâmetros em método/função
- **Problema:** API complexa, violação SRP
- **Exemplo:** `createUser(name, email, age, address, city, country, phone, cpf)`
- **Melhor:** `createUser(userDTO)`
- **Solução:** Introduce Parameter Object, Preserve Whole Object

ref: https://luzkan.github.io/smells/long-parameter-list

### Divergent Change
- **Sintoma:** Classe alterada por múltiplas razões não relacionadas
- **Problema:** Violação SRP, classe com responsabilidades demais
- **Exemplo:** `ReportGenerator` alterada quando: muda BD, muda formato, muda cálculo
- **Solução:** Extract Class, Move Method

ref: https://luzkan.github.io/smells/divergent-change

### Shotgun Surgery
- **Sintoma:** Uma mudança requer modificações em múltiplas classes
- **Problema:** Código espalhado, duplicação lógica
- **Exemplo:** Mudar validação de email requer alterar User, Order, Newsletter, Support...
- **Solução:** Move Method, Inline Class

ref: https://luzkan.github.io/smells/shotgun-surgery

### Feature Envy
- **Sintoma:** Método usa mais dados de outra classe que da própria
- **Problema:** Responsabilidade mal posicionada
- **Exemplo:**
```js
class Order {
  getTotal(customer) {
    return customer.items.reduce((sum, item) =>
      sum + item.price * customer.discount, 0);
  }
}
```
- **Solução:** Move Method, Extract Method

ref: https://luzkan.github.io/smells/feature-envy

### Data Clump
- **Sintoma:** Grupos de variáveis sempre usados juntos (ex: x,y,z; red,green,blue)
- **Problema:** Abstração oculta
- **Exemplo:** `drawCircle(x, y, z, radius)` → `drawCircle(point3D, radius)`
- **Solução:** Extract Class, Introduce Parameter Object

ref: https://luzkan.github.io/smells/data-clump

## 🔄 CONDICIONAL & CONTROLE

### Conditional Complexity (Switch Statements)
- **Sintoma:** Longos if/else ou switch/case cascateados
- **Problema:** Violação Open-Closed, difícil extensão
- **Exemplo:**
```js
if (type === 'admin') { ... }
else if (type === 'user') { ... }
else if (type === 'guest') { ... }
else if (type === 'moderator') { ... }
```
- **Solução:** Replace with Polymorphism, Strategy Pattern

ref: https://luzkan.github.io/smells/conditional-complexity

### Complicated Boolean Expression
- **Sintoma:** Expressões booleanas complexas e difíceis de ler
- **Problema:** Baixa legibilidade
- **Exemplo:** `if (!user.isActive && (user.age < 18 || !user.hasPermission) && !isWeekend())`
- **Melhor:** `if (shouldBlockAccess(user))`
- **Solução:** Introduce Explaining Variable, Extract Method

ref: https://luzkan.github.io/smells/complicated-boolean-expression

### Flag Argument
- **Sintoma:** Booleano como parâmetro controlando comportamento
- **Problema:** Método faz duas coisas, API confusa
- **Exemplo:** `book(customer, true)` // true o quê?
- **Melhor:** `bookPremium(customer)` ou `bookRegular(customer)`
- **Solução:** Split Method

ref: https://luzkan.github.io/smells/flag-argument

### Null Check
- **Sintoma:** Verificações null/undefined repetitivas
- **Problema:** Código poluído, duplicação
- **Exemplo:**
```js
if (user != null) {
  if (user.address != null) {
    if (user.address.city != null) {
      return user.address.city;
    }
  }
}
```
- **Solução:** Introduce Null Object, Use Optional/Maybe

ref: https://luzkan.github.io/smells/null-check

### Special Case
- **Sintoma:** Código tratando casos especiais com if/else
- **Problema:** Complexidade aumentada
- **Exemplo:** `if (customer.type === 'VIP') { specialPrice = price * 0.5; }`
- **Solução:** Replace with Polymorphism, Null Object Pattern

ref: https://luzkan.github.io/smells/special-case

## 📝 NOMES & NÚMEROS

### Magic Number
- **Sintoma:** Números literais sem contexto no código
- **Problema:** Sem significado semântico
- **Exemplo:** `if (status === 3) { ... }` ou `price * 0.15`
- **Melhor:** `if (status === STATUS_APPROVED)` ou `price * TAX_RATE`
- **Solução:** Replace with Symbolic Constant

ref: https://luzkan.github.io/smells/magic-number

### Uncommunicative Name
- **Sintoma:** Nomes como data, temp, obj, foo, x1
- **Problema:** Código incompreensível
- **Exemplo:** `const d = new Date(); const x1 = calc(d);`
- **Melhor:** `const orderDate = new Date(); const totalPrice = calculateTotal(orderDate);`
- **Solução:** Rename Method/Variable com nomes descritivos

ref: https://luzkan.github.io/smells/uncommunicative-name

### Boolean Blindness
- **Sintoma:** Booleanos sem contexto (filter(true) vs filter(KEEP))
- **Problema:** Ambiguidade semântica
- **Exemplo:** `filter(items, true)` // filtrar o quê?
- **Melhor:** `filter(items, FilterAction.KEEP)` ou `filter(items, FilterAction.DROP)`
- **Solução:** Introduce Enum/Type

ref: https://luzkan.github.io/smells/boolean-blindness

### Type Embedded in Name
- **Sintoma:** userString, nameStr, listArray
- **Problema:** Duplicação de informação
- **Exemplo:** `const userArray: User[] = []` ou `nameString: string`
- **Melhor:** `const users: User[] = []` ou `name: string`
- **Solução:** Remover tipo do nome quando óbvio

ref: https://luzkan.github.io/smells/type-embedded-in-name

### Inconsistent Names
- **Sintoma:** add(), insert(), append() fazendo a mesma coisa
- **Problema:** Quebra padrão mental
- **Exemplo:** `userList.add()`, `productList.insert()`, `cartList.append()`
- **Melhor:** Padronizar: `list.add()` em todos
- **Solução:** Padronizar nomenclatura

ref: https://luzkan.github.io/smells/inconsistent-names

## 🗑️ CÓDIGO DESNECESSÁRIO

### Dead Code
- **Sintoma:** Código não executado, comentado, após return
- **Problema:** Poluição, confusão
- **Exemplo:**
```js
function calc() {
  return total;
  console.log('nunca executa'); // dead code
  // const old = ...; // código comentado
}
```
- **Solução:** Deletar

ref: https://luzkan.github.io/smells/dead-code

### Duplicated Code
- **Sintoma:** Código idêntico ou similar em múltiplos lugares
- **Problema:** Manutenção duplicada
- **Exemplo:**
```js
// UserController
const validated = email && email.includes('@');
// OrderController
const validated = email && email.includes('@');
```
- **Melhor:** `validateEmail(email)` em um helper
- **Solução:** Extract Method, Pull Up Method

ref: https://luzkan.github.io/smells/duplicated-code

### Speculative Generality
- **Sintoma:** Classes/métodos para "futuro uso" nunca usado
- **Problema:** Complexidade desnecessária, YAGNI
- **Exemplo:** `class AnimalRepository extends Repository` // só existe Human, nunca outros animais
- **Solução:** Remover ou Simplificar

ref: https://luzkan.github.io/smells/speculative-generality

### Lazy Element
- **Sintoma:** Classe/método que não justifica existência
- **Problema:** Complexidade sem valor
- **Exemplo:** `class Wrapper { getValue() { return value; } }` // apenas wrapper desnecessário
- **Solução:** Inline Class/Method

ref: https://luzkan.github.io/smells/lazy-element

### Temporary Field
- **Sintoma:** Atributo usado apenas em contextos específicos
- **Problema:** Confusão sobre estado do objeto
- **Exemplo:**
```js
class Calculator {
  tempResult; // só usado em calculate(), não em outras operações
  calculate() { this.tempResult = x + y; }
}
```
- **Solução:** Extract Class, Move Method

ref: https://luzkan.github.io/smells/temporary-field

## 🔗 ACOPLAMENTO

### Message Chain
- **Sintoma:** a.getB().getC().getD().doSomething()
- **Problema:** Violação Law of Demeter, acoplamento
- **Exemplo:** `user.getAddress().getCity().getZipCode().format()`
- **Melhor:** `user.getFormattedZipCode()`
- **Solução:** Hide Delegate, Extract Method

ref: https://luzkan.github.io/smells/message-chain

### Middle Man
- **Sintoma:** Classe apenas delega para outra
- **Problema:** Indireção desnecessária
- **Exemplo:**
```js
class OrderManager {
  getTotal() { return this.order.getTotal(); }
  getItems() { return this.order.getItems(); }
  getCustomer() { return this.order.getCustomer(); }
}
```
- **Solução:** Remove Middle Man

ref: https://luzkan.github.io/smells/middle-man

### Insider Trading (Inappropriate Intimacy)
- **Sintoma:** Classes acessam mutuamente dados privados
- **Problema:** Alto acoplamento
- **Exemplo:**
```js
class A { manipulate(b) { b.privateData = x; } }
class B { manipulate(a) { a.privateData = y; } }
```
- **Solução:** Move Method/Field, Change Bidirectional to Unidirectional

ref: https://luzkan.github.io/smells/insider-trading

### Hidden Dependencies
- **Sintoma:** Classe usa globals ou singletons não óbvios
- **Problema:** Difícil teste, acoplamento oculto
- **Exemplo:**
```js
class UserService {
  save() { Database.getInstance().save(this.user); } // dependência oculta
}
```
- **Melhor:** Injetar database via construtor
- **Solução:** Inject Dependencies

ref: https://luzkan.github.io/smells/hidden-dependencies

### Global Data
- **Sintoma:** Variáveis globais compartilhadas
- **Problema:** Estado não controlado, difícil rastreamento
- **Exemplo:** `var currentUser; var appConfig;` // acessíveis de qualquer lugar
- **Solução:** Encapsulate Variable, Pass as Parameter

ref: https://luzkan.github.io/smells/global-data

## 🎯 PRINCÍPIOS SOLID

### Refused Bequest
- **Sintoma:** Subclasse não usa métodos herdados ou lança exceção
- **Problema:** Violação LSP (Liskov)
- **Exemplo:**
```js
class Bird { fly() {...} }
class Penguin extends Bird {
  fly() { throw new Error('Penguins cannot fly'); }
}
```
- **Solução:** Replace Inheritance with Delegation

ref: https://luzkan.github.io/smells/refused-bequest

### Dubious Abstraction
- **Sintoma:** Abstração no nível errado ou inconsistente
- **Problema:** Violação SRP, confusão conceitual
- **Exemplo:** `instrument.write("*RST")` // deveria ser `adapter.write()`
- **Solução:** Extract Class, Fix Abstraction Level

ref: https://luzkan.github.io/smells/dubious-abstraction

### Inappropriate Static
- **Sintoma:** Métodos static que deveriam ser de instância
- **Problema:** Dificulta teste e extensão
- **Exemplo:** `Calculator.add(a, b)` quando há diferentes tipos de cálculo
- **Melhor:** `calculator.add(a, b)` com polimorfismo
- **Solução:** Convert to Instance Method

ref: https://luzkan.github.io/smells/inappropriate-static

## ⚡ PERFORMANCE & COMPLEXIDADE

### Primitive Obsession
- **Sintoma:** Uso de primitivos onde objetos seriam apropriados
- **Problema:** Lógica espalhada, sem encapsulamento
- **Exemplo:** `const phone = "11999998888"; const cpf = "123.456.789-00";`
- **Melhor:** `const phone = new Phone("11999998888"); const cpf = new CPF("123.456.789-00");`
- **Solução:** Replace Data Value with Object

ref: https://luzkan.github.io/smells/primitive-obsession

### Combinatorial Explosion
- **Sintoma:** Número exponencial de classes/métodos para cobrir combinações
- **Problema:** Manutenção impossível
- **Exemplo:** `ShirtRedSmall, ShirtRedMedium, ShirtBlueLarge...` (cores × tamanhos)
- **Melhor:** `Shirt(Color, Size)` com composição
- **Solução:** Use Composition over Inheritance

ref: https://luzkan.github.io/smells/combinatorial-explosion

### Callback Hell
- **Sintoma:** Callbacks aninhados profundamente
- **Problema:** Código ilegível, difícil debug
- **Exemplo:**
```js
getData(function(a) {
  getMore(a, function(b) {
    getEvenMore(b, function(c) {
      done(c);
    });
  });
});
```
- **Solução:** Use Promises, Async/Await

ref: https://luzkan.github.io/smells/callback-hell

### Imperative Loops
- **Sintoma:** Loops com índices manuais, mutação de estado
- **Problema:** Propenso a erros, menos expressivo
- **Exemplo:** `for (let i = 0; i < arr.length; i++) { result.push(arr[i] * 2); }`
- **Melhor:** `const result = arr.map(x => x * 2);`
- **Solução:** Use map/filter/reduce, forEach

ref: https://luzkan.github.io/smells/imperative-loops

## 🔒 MUTABILIDADE

### Mutable Data
- **Sintoma:** Objetos/variáveis modificados após criação
- **Problema:** Bugs difíceis, estado imprevisível
- **Exemplo:**
```js
const user = { name: 'João', age: 25 };
updateUser(user); // modifica user internamente
console.log(user.age); // 26? 25? Incerto!
```
- **Melhor:** Retornar novo objeto ao invés de modificar
- **Solução:** Use Immutable Objects, Functional Approach

ref: https://luzkan.github.io/smells/mutable-data

### Side Effects
- **Sintoma:** Método faz mais que o nome sugere
- **Problema:** Violação SRP, comportamento inesperado
- **Exemplo:**
```js
function setPrice(price) {
  this.price = price;
  this.sendEmailToCustomer(); // side effect inesperado!
  this.updateInventory(); // mais side effect!
}
```
- **Solução:** Separate Query from Command

ref: https://luzkan.github.io/smells/side-effects

### Afraid to Fail
- **Sintoma:** Retornar códigos de erro ao invés de exceções
- **Problema:** Verificações extras, poluição
- **Exemplo:** `const result = createUser(); if (result.error) {...}`
- **Melhor:** `try { createUser(); } catch(e) {...}`
- **Solução:** Fail Fast, Throw Exceptions

ref: https://luzkan.github.io/smells/afraid-to-fail

## 📋 ESTILO & ORGANIZAÇÃO

### Inconsistent Style
- **Sintoma:** Formatação/estilo varia no código
- **Problema:** Dificulta leitura e navegação
- **Exemplo:**
```js
function foo(a,b,c){return a+b+c}
function bar(x, y, z) {
  return x + y + z;
}
```
- **Solução:** Adotar linter/formatter

ref: https://luzkan.github.io/smells/inconsistent-style

### Clever Code
- **Sintoma:** Código "esperto" difícil de entender
- **Problema:** Manutenibilidade comprometida
- **Exemplo:** `x ^= y ^= x ^= y;` // swap usando XOR
- **Melhor:** `[x, y] = [y, x];` ou `temp = x; x = y; y = temp;`
- **Solução:** Simplificar, usar built-ins

ref: https://luzkan.github.io/smells/clever-code

### Obscured Intent
- **Sintoma:** Impossível entender o que código faz
- **Problema:** Manutenção impossível
- **Exemplo:** `const m_ot = i_t_w * i_t_r + (0.5 * i_t_r * max(0, i_t_w - 400));`
- **Solução:** Refatorar com nomes claros

ref: https://luzkan.github.io/smells/obscured-intent

### Indecent Exposure
- **Sintoma:** Campos/métodos públicos que deveriam ser privados
- **Problema:** Quebra encapsulamento
- **Exemplo:**
```js
class BankAccount {
  balance; // público, pode ser alterado diretamente
  withdraw(amount) { this.balance -= amount; }
}
```
- **Melhor:** `#balance` (privado) com getters/setters
- **Solução:** Use Proper Access Control

ref: https://luzkan.github.io/smells/indecent-exposure

---
**REGRA DE OURO:** Código bom é código que outro desenvolvedor (ou você em 6 meses) consegue entender rapidamente.
