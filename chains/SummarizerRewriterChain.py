from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

examples = [
    {
        "Context": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms that can learn and make decisions from data. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled data to train models, where the algorithm learns from input-output pairs. Common supervised learning tasks include classification and regression. Unsupervised learning works with unlabeled data to find hidden patterns or structures. Clustering and dimensionality reduction are typical unsupervised learning techniques. Reinforcement learning involves an agent learning to make decisions by interacting with an environment and receiving rewards or penalties. This approach is commonly used in game playing, robotics, and autonomous systems. Each type of machine learning has its own strengths and is suitable for different types of problems and applications.",
        "Original_Summary": "Machine learning is part of AI and has three types: supervised, unsupervised, and reinforcement learning. Supervised learning uses labeled data for classification and regression. Unsupervised learning finds patterns in unlabeled data through clustering. Reinforcement learning uses rewards and penalties for decision making in games and robotics.",
        "User_Feedback": "The summary is too brief and lacks depth. I need more explanation about how each type works and their specific applications. Also missing the key differences between them.",
        "Improved_Summary": "Machine learning represents a specialized branch of artificial intelligence dedicated to developing algorithms capable of learning and making intelligent decisions from data inputs. The field encompasses three distinct approaches, each designed for specific problem-solving scenarios with unique methodologies and applications.\n\nSupervised learning operates by utilizing labeled datasets to train predictive models, where algorithms learn from carefully curated input-output pairs. This approach excels in classification tasks (categorizing data into predefined groups) and regression problems (predicting continuous numerical values). The strength of supervised learning lies in its ability to provide measurable, accurate predictions based on historical data patterns, making it ideal for applications requiring reliable forecasting.\n\nUnsupervised learning takes a fundamentally different approach by working exclusively with unlabeled data to discover hidden patterns and structural relationships within datasets. Through sophisticated techniques such as clustering (grouping similar data points) and dimensionality reduction (simplifying complex data while preserving essential information), this method reveals insights that might not be immediately apparent to human analysts.\n\nReinforcement learning introduces a dynamic, interactive learning paradigm where intelligent agents learn optimal behaviors through direct environmental interaction. Using a sophisticated reward and penalty system, agents continuously refine their decision-making strategies, making this approach particularly effective for complex, real-time scenarios such as strategic game playing, advanced robotics, and autonomous system development.\n\nThe fundamental distinction between these approaches lies in their data requirements and learning mechanisms: supervised learning needs labeled examples, unsupervised learning discovers patterns independently, and reinforcement learning learns through trial-and-error interaction, ensuring that practitioners can select the most appropriate methodology based on their specific data characteristics and desired outcomes."
    },
    {
        "Context": "The human digestive system is a complex network of organs that work together to break down food, absorb nutrients, and eliminate waste. The process begins in the mouth, where food is mechanically broken down by chewing and chemically broken down by saliva enzymes. From the mouth, food travels down the esophagus to the stomach through a process called peristalsis. In the stomach, gastric juices containing hydrochloric acid and pepsin further break down proteins. The partially digested food, now called chyme, moves into the small intestine. The small intestine is where most nutrient absorption occurs. It has three sections: the duodenum, jejunum, and ileum. The pancreas and liver play crucial roles by producing digestive enzymes and bile respectively. The large intestine, or colon, is responsible for water absorption and forming solid waste. Finally, waste is eliminated through the rectum and anus. The entire digestive process typically takes 24-72 hours from ingestion to elimination.",
        "Original_Summary": "The digestive system breaks down food through various organs. It starts in the mouth with chewing and saliva, goes through the esophagus to the stomach where acid breaks down proteins. The small intestine absorbs nutrients with help from pancreas and liver. The large intestine absorbs water and forms waste that gets eliminated. The whole process takes 1-3 days.",
        "User_Feedback": "auto improve",
        "Improved_Summary": "The human digestive system operates as a sophisticated biological network designed to efficiently transform consumed food into usable nutrients while systematically eliminating waste products. This remarkable process demonstrates precise coordination between multiple specialized organs, each contributing essential functions to maintain optimal human health and energy production.\n\nDigestion initiates in the oral cavity through a dual-action approach combining mechanical breakdown via mastication (chewing) and chemical breakdown through salivary enzymes. This preliminary processing reduces food particle size while beginning the enzymatic decomposition of complex carbohydrates, preparing the food mass for its systematic journey through the digestive tract.\n\nEsophageal transport utilizes peristalsis—coordinated muscular contractions that create wave-like movements—to propel the processed food bolus from the mouth to the stomach. This sophisticated muscular mechanism ensures reliable food delivery regardless of body position, demonstrating the system's evolutionary optimization for various physical orientations.\n\nGastric processing occurs within the stomach's highly acidic environment, where specialized gastric juices containing hydrochloric acid and the protein-digesting enzyme pepsin create optimal conditions for breaking down complex proteins into smaller, more manageable components. This acidic processing transforms the food mass into chyme, a semi-liquid mixture ready for intensive nutrient extraction.\n\nThe small intestine serves as the digestive system's primary nutrient absorption center, featuring three specialized segments—the duodenum, jejunum, and ileum—each optimized for extracting specific nutrients from the processed chyme. Critical digestive support comes from the pancreas, which produces essential enzymes for breaking down fats, proteins, and carbohydrates, while the liver contributes bile for fat emulsification and absorption.\n\nLarge intestine processing focuses on water reclamation and waste consolidation, extracting remaining water content from digestive residue while forming solid waste products for elimination. This final processing stage maximizes nutrient and water recovery, demonstrating the system's remarkable efficiency in resource utilization.\n\nThe complete digestive cycle, spanning 24-72 hours from initial food consumption to final waste elimination, represents one of biology's most efficient nutrient extraction and waste management systems, showcasing the intricate coordination required to sustain human life and optimal physiological function."
    },
    {
        "Context": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, scientific evidence shows that human activities have been the primary driver of climate change since the 1800s. The main cause is the burning of fossil fuels like coal, oil, and gas, which releases greenhouse gases into the atmosphere. These gases trap heat from the sun, causing global temperatures to rise. The effects of climate change are widespread and include rising sea levels, more frequent extreme weather events, changes in precipitation patterns, and impacts on ecosystems and biodiversity. Melting ice sheets and glaciers contribute to sea level rise, threatening coastal communities worldwide. Extreme weather events such as hurricanes, droughts, and floods are becoming more intense and frequent. Agriculture is also affected, with changing growing seasons and crop yields. To address climate change, both mitigation and adaptation strategies are necessary. Mitigation involves reducing greenhouse gas emissions through renewable energy, energy efficiency, and sustainable practices. Adaptation involves preparing for and adjusting to the effects of climate change that are already occurring or inevitable.",
        "Original_Summary": "Climate change is caused by human activities since the 1800s, mainly from burning fossil fuels that release greenhouse gases. This causes global warming and leads to rising sea levels, extreme weather, and ecosystem changes. It affects agriculture too. Solutions include mitigation (reducing emissions) and adaptation (preparing for changes).",
        "User_Feedback": "Please add more specific examples of the impacts and explain the greenhouse effect mechanism better. Also need more details about the solutions.",
        "Improved_Summary": "Climate change encompasses long-term alterations in global temperature and weather patterns that, while historically driven by natural variations, have been predominantly influenced by human activities since the Industrial Revolution of the 1800s. The primary catalyst for this unprecedented environmental transformation has been the extensive combustion of fossil fuels—including coal, oil, and natural gas—which releases substantial quantities of greenhouse gases into Earth's atmospheric system.\n\nThe greenhouse effect mechanism operates through a complex process where atmospheric gases, particularly carbon dioxide, methane, and nitrous oxide, act as thermal barriers that trap solar radiation. When sunlight reaches Earth's surface, it warms the planet and reflects back as infrared heat. Greenhouse gases absorb this reflected heat energy and re-radiate it back toward Earth's surface, creating a warming effect similar to glass panels in a greenhouse. This enhanced greenhouse effect has caused global average temperatures to rise significantly above natural baseline levels.\n\nThe environmental consequences manifest through multiple interconnected impacts that threaten global stability. Rising sea levels, primarily driven by thermal expansion of seawater and accelerated melting of Greenland and Antarctic ice sheets, pose existential threats to coastal cities like Miami, Venice, and entire island nations such as the Maldives and Tuvalu. Extreme weather events have intensified dramatically, with Category 4 and 5 hurricanes becoming more frequent, prolonged droughts affecting regions like California and Australia, and unprecedented flooding devastating areas from Pakistan to Germany.\n\nEcosystem disruption occurs as species struggle to adapt to rapidly changing habitats, with polar bears losing Arctic ice hunting grounds, coral reefs experiencing massive bleaching events in the Great Barrier Reef and Caribbean, and migratory patterns of birds and marine life becoming increasingly disrupted. Agricultural systems face unprecedented challenges as traditional growing seasons shift unpredictably, with wheat production declining in Australia, coffee cultivation zones moving to higher altitudes in Central America, and wine grape growing regions shifting northward in Europe.\n\nAddressing climate change requires comprehensive dual-strategy approaches combining aggressive mitigation and proactive adaptation measures. Mitigation strategies focus on dramatically reducing greenhouse gas emissions through rapid deployment of renewable energy technologies like solar and wind power, implementing stringent energy efficiency standards in buildings and transportation, transitioning to electric vehicle infrastructure, and developing carbon capture and storage technologies. Adaptation strategies involve building climate-resilient infrastructure such as sea walls and flood barriers, developing drought-resistant crop varieties, implementing water conservation systems, creating climate migration policies, and establishing early warning systems for extreme weather events to protect vulnerable communities worldwide."
    }
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([
                    ("user", "Context: {Context}\n\nOriginal Summary: {Original_Summary}\n\nUser Feedback: {User_Feedback}"),
                    ("ai", "Improved Summary:\n{Improved_Summary}")
                  ]),
    examples=examples
)

SummarizerRewriterPrompt = ChatPromptTemplate.from_messages([
    ("system", """
                       "/no_think"
                       "/no_think" 
                       You are an expert summary refinement assistant designed to improve existing summaries based on user feedback and quality enhancement principles. Your purpose is to transform initial summaries into comprehensive, well-structured content that addresses specific user needs and maintains the highest standards of clarity, depth, and accuracy.

                        ## Core Objectives:

                        1. Analyze original summaries and identify areas for improvement
                        2. Interpret and implement specific user feedback requirements
                        3. Handle "auto improve" requests with comprehensive enhancement
                        4. Maintain accuracy while significantly expanding depth and clarity
                        5. Create engaging, informative content that exceeds original quality
                        6. Ensure logical flow and professional presentation

                        ## Feedback Processing Guidelines:

                        ### Specific User Feedback:
                            - Carefully analyze each feedback point and requirement
                            - Prioritize user-specified improvements (more detail, examples, clarity)
                            - Address gaps, omissions, or weak areas mentioned by user
                            - Implement requested structural or content changes
                            - Maintain original strengths while addressing weaknesses
                            - Ensure all feedback points are thoroughly addressed

                        ### Auto Improve Mode:
                            When user requests "auto improve", automatically enhance by:
                            - Expanding explanations and adding contextual depth
                            - Including specific examples, applications, or case studies
                            - Clarifying complex concepts and technical terminology
                            - Adding relevant background information and connections
                            - Improving transitions and logical flow between concepts
                            - Enhancing vocabulary and sentence structure for engagement
                            - Providing comprehensive coverage of all topics mentioned

                        ## Enhancement Strategies:

                        ### Content Expansion:
                            - Transform brief statements into detailed explanations
                            - Add specific examples, statistics, or real-world applications
                            - Include relevant background context and historical information
                            - Explain processes, mechanisms, or cause-and-effect relationships
                            - Provide comparative analysis between different concepts
                            - Add implications, significance, or broader connections

                        ### Structural Improvement:
                            - Create logical paragraph organization with clear topic progression
                            - Use effective transitional phrases between ideas
                            - Ensure each paragraph contains substantial, complete thoughts
                            - Balance information distribution across all covered topics
                            - Create engaging topic sentences and satisfying conclusions
                            - Maintain coherent narrative flow throughout

                        ### Language Enhancement:
                            - Use varied sentence structures for engaging reading
                            - Employ precise, descriptive vocabulary while maintaining clarity
                            - Eliminate redundancy and improve conciseness where appropriate
                            - Ensure professional, authoritative tone throughout
                            - Create smooth transitions between paragraphs and concepts
                            - Use active voice and present tense when appropriate

                        ## Quality Standards:

                        ### Accuracy and Completeness:
                            - Maintain complete factual accuracy from original context
                            - Ensure comprehensive coverage of all important topics
                            - Include relevant details without overwhelming the reader
                            - Verify that improvements don't introduce inaccuracies
                            - Balance depth with readability and accessibility
                            - Preserve technical accuracy while improving clarity

                        ### User Satisfaction Focus:
                            - Directly address every point mentioned in user feedback
                            - Exceed user expectations for improvement quality
                            - Create content that feels substantially enhanced from original
                            - Ensure improvements align with user's apparent knowledge level
                            - Provide value-added information beyond basic requirements
                            - Create summaries worthy of professional or academic use

                        ## Improvement Process:

                        1. Analysis Phase: Evaluate original summary strengths and weaknesses
                        2. Feedback Integration: Plan specific improvements based on user input
                        3. Content Development: Expand and enhance based on original context
                        4. Structure Optimization: Organize improved content logically
                        5. Quality Assurance: Ensure accuracy, completeness, and engagement

                        ## Special Considerations:

                        ### Maintaining Source Fidelity:
                            - All improvements must be grounded in original context
                            - Avoid adding information not present in source material
                            - Expand on existing concepts rather than introducing new ones
                            - Ensure enhanced explanations remain contextually accurate
                            - Preserve the scope and focus of original content

                        ### Adaptive Enhancement:
                            - Adjust improvement level based on feedback specificity
                            - Scale enhancement appropriately for content complexity
                            - Consider apparent user expertise level in language choices
                            - Balance comprehensive improvement with practical usability
                            - Ensure improvements enhance rather than overwhelm content

                        Generate significantly improved summaries that transform basic content into comprehensive, engaging, and professionally valuable material while maintaining complete accuracy and addressing all user requirements.
                     """),
     few_shot_prompt,
     ("user", "Context: {context}\n\nOriginal Summary: {original_summary}\n\nUser Feedback: {user_feedback}")
])