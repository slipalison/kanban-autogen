# MudBlazor - Guia de Componentes e Setup

### 1. Instalação e Configuração
- **NuGet:** `dotnet add package MudBlazor`
- **Program.cs:** `builder.Services.AddMudServices();`
- **_Imports.razor:** `@using MudBlazor`
- **Layout:** Adicionar `<MudThemeProvider />`, `<MudPopoverProvider />`, `<MudDialogProvider />`, `<MudSnackbarProvider />` no `App.razor` ou `MainLayout.razor`.

### 2. Layout e Navegação
- **Estrutura:** `<MudLayout>`, `<MudAppBar>`, `<MudDrawer>`, `<MudMainContent>`, `<MudNavMenu>`, `<MudNavLink>`.
- **Exemplo Sidebar:**
```razor
<MudNavMenu>
    <MudNavLink Href="/" Icon="@Icons.Material.Filled.Dashboard">Dashboard</MudNavLink>
    <MudNavGroup Title="Settings" Icon="@Icons.Material.Filled.Settings">
        <MudNavLink Href="/profile">Profile</MudNavLink>
    </MudNavGroup>
</MudNavMenu>
```

### 3. Formulários e Inputs
- **MudForm:** `@ref="_form"`, `@bind-IsValid="_isValid"`.
- **Inputs:** `MudTextField`, `MudSelect`, `MudCheckBox`, `MudSwitch`, `MudDatePicker`, `MudAutocomplete`.
- **Validação:** `Required="true"`, `Validation="@(new Func<string, string>(Validate))"`.

### 4. Exibição de Dados
- **MudDataGrid:** Suporta ordenação, filtragem e agrupamento.
```razor
<MudDataGrid Items="@_items">
    <Columns>
        <PropertyColumn Property="x => x.Name" Title="Nome" />
        <TemplateColumn>
            <CellTemplate><MudButton>Edit</MudButton></CellTemplate>
        </TemplateColumn>
    </Columns>
</MudDataGrid>
```
- **MudTable:** Versão mais leve para tabelas simples.

### 5. Diálogos e Notificações (Serviços)
- **Snackbar:** `ISnackbar.Add("Mensagem", Severity.Success);`
- **Diálogos:** `IDialogService.Show<Component>("Título");`
- **MessageBox:** `DialogService.ShowMessageBox("Confirma?", "Ação crítica", yesText:"Ok");`

### 6. Componentes de UI
- **MudButton:** `Variant="Variant.Filled"`, `Color="Color.Primary"`.
- **MudCard:** `<MudCardHeader>`, `<MudCardContent>`, `<MudCardActions>`.
- **MudTabs:** `<MudTabs>`, `<MudTabPanel>`.
- **MudProgressCircular:** `Indeterminate="true"`.

### 7. Drag & Drop (Kanban)
- **MudDropContainer:** Container principal. `Items`, `ItemsSelector`, `ItemUpdated`.
- **MudDropZone:** Zona de soltura. `Identifier`.
- **Exemplo Estrutura:**
```razor
<MudDropContainer T="KanbanItem" Items="@_items" ItemsSelector="@((item, zone) => item.Status == zone)" ItemUpdated="ItemUpdated">
    <ChildContent>
        <MudDropZone T="KanbanItem" Identifier="Todo" Class="flex-grow-1" />
    </ChildContent>
    <ItemRenderer>
        <MudCard>@context.Title</MudCard>
    </ItemRenderer>
</MudDropContainer>
```
- **Lógica C#:** `void ItemUpdated(MudItemDropInfo<KanbanItem> info) => info.Item.Status = info.DropzoneIdentifier;`
